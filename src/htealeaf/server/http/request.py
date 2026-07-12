import json
from dataclasses import dataclass
from tempfile import SpooledTemporaryFile
from typing import TYPE_CHECKING, Any, AsyncGenerator, Awaitable, Callable, Optional

from python_multipart import MultipartParser

from htealeaf.server.http.utils import get_boundary, parse_content_disposition

from .header import Headers

if TYPE_CHECKING:
    from python_multipart.multipart import MultipartCallbacks


class HttpRequest:
    """
    Represents an HTTP request with attributes for method, path, headers, and body.
    """

    def __init__(
        self,
        method: str = "GET",
        path: str = "/",
        args: dict[str, str] = {},
        headers: list[tuple[str, str]] | dict[str, str] = [],
        body: bytes | None = None,
        body_handler: Callable[[], Awaitable[dict[str, Any]]] | None = None,
        is_ssl: bool = False,
    ):

        self.method: str = method
        self.path: str = path
        self.args: dict[str, str] = args
        self.headers: Headers = Headers(headers)
        self.body: bytes | None = body
        self._body_handler = body_handler
        self.is_stream = body_handler is not None
        self.is_ssl = is_ssl

    async def stream(self) -> AsyncGenerator[bytes, None]:
        assert self.body is not None

        yield self.body

        if self._body_handler is None:
            return

        while True:
            event = await self._body_handler()
            yield event["body"]
            if not event.get("more_body", False):
                break

    async def multipart(self, spool_limit: int = 1024 * 1024) -> dict[str, str]:
        parts = {}
        current = {"headers": [], "buf": None, "is_file": False}

        def on_part_begin():
            current["buf"] = SpooledTemporaryFile(max_size=spool_limit)
            current["headers"] = []
            current["is_file"] = False

        def on_header_field(data, start, end):
            current["headers"].append((data[start:end].decode("utf-8"), ""))

        def on_header_value(data, start, end):
            current["headers"][-1] = (
                current["headers"][-1][0],
                data[start:end].decode("utf-8"),
            )
            if current["headers"][-1][0] == "Content-Disposition":
                current["is_file"] = "filename" in current["headers"][-1][1]

        def on_part_data(data, start, end):
            current["buf"].write(data[start:end])

        def on_part_end():
            buf = current["buf"]
            buf.seek(0)

            disposition = next(
                (
                    v
                    for k, v in current["headers"]
                    if k.lower() == "content-disposition"
                ),
                "",
            )

            name, filename = parse_content_disposition(disposition)
            if name is None:
                raise ValueError(
                    "Content-Disposition header is missing 'name' parameter"
                )
            if current["is_file"]:
                content_type = next(
                    (v for k, v in current["headers"] if k.lower() == "content-type"),
                    None,
                )
                assert filename is not None  # review if filename is always available
                parts[name] = UploadFile(
                    filename=filename, content_type=content_type, file=buf
                )
            else:
                parts[name] = buf.read().decode("utf-8")
                buf.close()

        callbacks: MultipartCallbacks = {
            "on_part_begin": on_part_begin,
            "on_header_field": on_header_field,
            "on_header_value": on_header_value,
            "on_part_data": on_part_data,
            "on_part_end": on_part_end,
        }

        content_type = self.headers.get("content-type")
        if content_type is None:
            raise ValueError("No content-type header")
        boundary = get_boundary(content_type)
        parser = MultipartParser(boundary, callbacks)
        try:
            async for chunk in self.stream():
                parser.write(chunk)
            parser.finalize()
        except Exception:
            raise

        return parts

    def text(self) -> str | None:
        return self.__body_to_text__()

    def __body_to_text__(self) -> str | None:
        content_length = self.headers.get("content-length")
        if content_length is None:
            return None

        try:
            body_size = int(content_length)
        except (TypeError, ValueError):
            return None
        if body_size <= 0 or self.body is None:
            return None

        if isinstance(self.body, str):
            return self.body
        elif isinstance(self.body, bytes):
            raw = self.body
        elif hasattr(self.body, "__iter__"):
            raw = b"".join([d for d in iter(self.body)])
        else:
            raise ValueError(f"Invalid body type: {type(self.body)}")

        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return None

    def form(self) -> dict[str, str] | None:
        """
        Parses form-encoded body data into a dictionary.

        Returns:
            dict[str, str] | None: A dictionary of form values or None if invalid.
        """
        if self.body is None:
            return None
        body = self.body.decode("utf-8")
        if body is None:
            return None
        return dict(item.split("=", 1) for item in body.split("&") if "=" in item)

    def json(self) -> Optional[dict]:
        """
        Parses the request body as JSON.

        Returns:
            dict | None: A dictionary representation of the JSON body or None if invalid.
        """

        if self.body is None:
            return None
        body = self.body.decode("utf-8")

        try:
            return json.loads(body)
        except (json.JSONDecodeError, AttributeError):
            return None


@dataclass
class UploadFile:
    filename: str
    content_type: str | None
    file: SpooledTemporaryFile

    def read(self, size: int = -1) -> bytes:
        return self.file.read(size)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self.file.seek(offset, whence)

    @property
    def size(self) -> int:
        pos = self.file.tell()
        self.file.seek(0, 2)
        size = self.file.tell()
        self.file.seek(pos)
        return size

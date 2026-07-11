import io
import json
from typing import Any, Optional, Callable, Awaitable


from .header import Headers


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
        is_ssl: bool = False
    ):

        self.method: str = method
        self.path: str = path
        self.args: dict[str, str] = args
        self.headers: Headers = Headers(headers)
        self.body: bytes | None = body
        self._body_handler = body_handler
        self.is_stream = body_handler is not None
        self.is_ssl = is_ssl

    async def stream(self):

        yield self.body

        if self._body_handler is None:
            return

        while True:
            event = await self._body_handler()
            yield event["body"]
            if not event.get("more_body", False):
                break




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
        elif isinstance(self.body, io.BufferedReader):
            if self.body.closed or not self.body.readable():
                return None
            raw = self.body.read(body_size)
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

        body = self.__body_to_text__()
        if body is None:
            return None
        return dict(item.split("=", 1) for item in body.split("&") if "=" in item)

    def json(self) -> Optional[dict]:
        """
        Parses the request body as JSON.

        Returns:
            dict | None: A dictionary representation of the JSON body or None if invalid.
        """

        body = self.__body_to_text__()
        if body is None:
            return None
        try:
            return json.loads(body)
        except (json.JSONDecodeError, AttributeError):
            return None

import json
from typing import Any, Awaitable, Callable, Optional

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
        if self.body is None:
            return None
        return self.body.decode("utf-8")

    # def multipart(self) -> dict[str, str] | None:
    #     if self._type is None or not self._type.startswith("multipart/form-data"):
    #         return None
    #     if self._raw is None:
    #         return None

    #     separator = self._type.split("boundary=")[1].encode()

    #     result = {}

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


# body transform

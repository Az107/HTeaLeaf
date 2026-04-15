
import io
import json
from typing import Any, Optional

from .HttpHeader import Headers

class HttpRequest:
    """
    Represents an HTTP request with attributes for method, path, headers, and body.
    """

    def __init__(
        self,
        method: str = "GET",
        path: str = "/",
        args: dict[str, str] = {},
        headers: list[tuple[str, str]] | dict[str,str] = [],
        body: str | bytes | io.BufferedReader | None = None,
    ):

        self.method: str = method
        self.path: str = path
        self.args: dict[str, str] = args
        self.headers: Headers = Headers(headers)
        self.body: str | bytes | io.BufferedReader | Any | None = body

    def text(self) -> str | None:
        return self.__body_to_text__()

    def __body_to_text__(self) -> str | None:
        content_length =  self.headers.get("content-length")
        if content_length is None:
            return None

        body_size = int(content_length or 0)
        if body_size == 0 or self.body is None:
            return None
        if isinstance(self.body, io.BufferedReader):
            if not self.body.closed and self.body.readable():
                return self.body.read(body_size).decode("utf-8")
            else:
                return None
        elif isinstance(self.body, bytes):
            return self.body.decode("utf-8")
        elif isinstance(self.body, str):
            return self.body
        elif hasattr(self.body, '__iter__'):
            result = b"".join([d for d in iter(self.body)])
            return result.decode("utf-8")
        else:
            raise ValueError(f"Invalid body type: {type(self.body)}")

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

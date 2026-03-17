
from typing import Iterator

from ..Html.Component import Component
from .Http.HttpHeader import Headers
from .Server import HttpRequest, Server


def to_list(headers: Headers) -> list[tuple[str, str]]:
    return [h for h in headers]

class WSGI(Server):
    def __init__(self):
        super().__init__()



    def wsgi_app(self, environ: dict[str,str], start_response) -> Iterator[bytes]:
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        headers = {}
        try:
            headers["content_length"] = int(environ.get("CONTENT_LENGTH", 0))  # Puede ser None o vacío
        except ValueError:
            headers["content_length"] = 0
        for k in environ:
            if k.startswith("HTTP_"):
                headers[k[5:]] = environ[k]
        body = environ.get('wsgi.input',"body")
        request = HttpRequest(method,path,headers=headers,body=body)
        response = self.handle_request(request)
        start_response(response.status.to_str(), to_list(response.headers))
        response_body: bytes = response.body.encode("utf-8") if isinstance(response.body, str) else response.body
        return iter([response_body])

    def serve(self, payload: str | Component):
        return super().serve(payload)

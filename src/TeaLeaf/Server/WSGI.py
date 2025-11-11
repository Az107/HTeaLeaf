
from .Server import HttpRequest, Server

from ..Html.Component import Component

class WSGI(Server):
    def __init__(self):
        super().__init__()


    def wsgi_app(self, environ: dict[str,str], start_response):
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
        status, headers, body = self.handle_request(request)
        start_response(status, headers)
        return iter([b.encode('utf-8') for b in body])

    def serve(self, payload: str | Component):
        return super().serve(payload)

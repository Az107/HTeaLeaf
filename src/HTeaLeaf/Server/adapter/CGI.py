import os
import sys
from types import FunctionType
from urllib.parse import parse_qs

from ..Http import Request, Response


def CGI(handler: FunctionType):
    raise Exception("Not implemented")

    def application(self) -> None:
        input_data = sys.stdin.read()

        query_string = os.environ.get("QUERY_STRING", "")
        method = os.environ.get("REQUEST_METHOD", "")
        cgi_vars: dict[str, object] = dict()

        if query_string:
            cgi_vars.update(parse_qs(query_string))

        if method == "POST" and input_data:
            cgi_vars.update(parse_qs(input_data))

        # Obtener algunas variables de entorno comunes
        cgi_vars["REQUEST_METHOD"] = method
        cgi_vars["CONTENT_TYPE"] = os.environ.get("CONTENT_TYPE", "")
        cgi_vars["QUERY_STRING"] = query_string
        cgi_vars["PATH_INFO"] = os.environ.get("PATH_INFO", "")
        cgi_vars["SCRIPT_NAME"] = os.environ.get("SCRIPT_NAME", "")
        cgi_vars["SCRIPT_FILENAME"] = os.environ.get("SCRIPT_FILENAME", "")

        request = Request(
            method,
        )
        response: Response = handler(request)
        for k in response.headers:
            print(f"{k}: {response.headers[k]}")
        print("\r\n")

        # def serve(self, payload: str | Component):
        #     headers: dict[str, str] = dict()
        #     content = payload
        #     if isinstance(payload, Component):
        #         try:
        #             content = payload.render()
        #         except Exception:
        #             print("<h1>500 Internal Server Error</h1>")
        #     print(content)

    return application

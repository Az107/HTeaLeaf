import os
import sys
from urllib.parse import parse_qs

from .Server import Server
from ..Html.Component import Component


class CGI(Server):
    def __init__(self) -> None:
        super().__init__()
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

        self.method = method
        self.server_vars = cgi_vars

    def serve(self, payload: str | Component):
        headers: dict[str, str] = dict()
        for k in headers:
            print(f"{k}: {headers[k]}")
        print("\r\n")
        content = payload
        if isinstance(payload, Component):
            try:
                content = payload.render()
            except Exception:
                print("<h1>500 Internal Server Error</h1>")
        print(content)

import os
import sys
from types import FunctionType
from urllib.parse import parse_qs, parse_qsl

from HTeaLeaf.Server.Http.HttpHeader import Headers

from ..Http import Request, Response
from .adapter import adapter

@adapter
def CGI(handler: FunctionType):
        input_data = sys.stdin.read()

        query_string = os.environ.get("QUERY_STRING", "")
        method = os.environ.get("REQUEST_METHOD", "")
        cgi_vars: dict[str, object] = dict()

        if query_string:
            cgi_vars.update(parse_qs(query_string))

        if method == "POST" and input_data:
            cgi_vars.update(parse_qs(input_data))


        cgi_vars["REQUEST_METHOD"] = method
        cgi_vars["CONTENT_TYPE"] = os.environ.get("CONTENT_TYPE", "")
        cgi_vars["QUERY_STRING"] = query_string
        cgi_vars["PATH_INFO"] = os.environ.get("PATH_INFO", "")
        cgi_vars["SCRIPT_NAME"] = os.environ.get("SCRIPT_NAME", "")
        cgi_vars["SCRIPT_FILENAME"] = os.environ.get("SCRIPT_FILENAME", "")

        SPECIAL = {"CONTENT_TYPE", "CONTENT_LENGTH"}

        headers = {}
        for key, value in os.environ.items():
            if key in SPECIAL:
                headers[key.replace("_", "-").title()] = value
            elif key.startswith("HTTP_"):
                headers[key[5:].replace("_", "-").title()] = value
        request = Request(
            method,
            cgi_vars["PATH_INFO"],
            dict(parse_qsl(query_string)),
            headers,
            input_data
        )
        response: Response = handler(request)
        for k,v in response.headers:
            sys.stdout.buffer.write(f"{k}: {v}\n".encode())
        sys.stdout.buffer.write(b"\r\n")
        print(response.body)

import asyncio
import contextvars
import functools
import inspect
import json
import os
import re
import typing
from enum import Enum
from threading import local
from typing import Callable

from htealeaf.error import RenderError, ServerError, SourceLocation

from ..elements.component import Component
from ..elements.renderer import HTMLRenderer, init_render_ctx
from ..state.helper_midleware import insert_helper_script
from .adapter import ASGI
from .http import Headers, Request, Response, Status
from .session import SessionManager

COOKIE_NAME = "HTeaLeaf-Session"


def path_to_regex(path: str) -> str:
    """
    Converts a path with curly braces and optional wildcards into a regex pattern.

    Examples:
        "/users/{id}"      -> "^/users/(?P<id>[^/]+)$"
        "/test/{id}/*"     -> "^/test/(?P<id>[^/]+)(?:/.*)?$"
        "/foo/*/bar"       -> "^/foo/.*/bar$"

    Args:
        path (str): The path pattern with placeholders and/or wildcards.

    Returns:
        str: The equivalent regex pattern.
    """

    # Sustituimos {param} por grupos con nombre
    regex = re.sub(r"\{([^}]+)\}", r"(?P<\1>[^/]+)", path)

    # Sustituimos '*' por un patrón que capture el resto del path
    regex = regex.replace("*", ".*")

    # Si acaba en '.*' (wildcard final), permitimos que sea opcional
    if regex.endswith(".*"):
        regex = regex[:-2] + "(?:.*)?"

    return f"^{regex}$"


def extract_wildcards(path_regex: str, url: str) -> dict | None:
    """
    Extracts wildcard values from a given regex pattern and a matching URL.

    Args:
        path_regex (str): The compiled regex pattern.
        url (str): The incoming request URL.

    Returns:
        dict | None: A dictionary of extracted values or None if no match.
    """
    match = re.match(path_regex, url)
    if match:
        return match.groupdict()  # Devuelve un diccionario con los valores capturados
    return None


def match_path(
    routes: dict[str, typing.Callable], path: str
) -> tuple[dict[str, str | object], typing.Callable] | None:
    """
    Matches a given path against registered route patterns.

    Args:
        routes (dict[str, Callable]): A dictionary mapping regex patterns to handlers.
        path (str): The request path.

    Returns:
        tuple[dict, Callable] | None: Matched parameters and handler function, or None if no match.
    """

    for regex, value in routes.items():
        match = re.match(regex, path)
        if match:
            return match.groupdict(), value
    return None


def return_helper():
    try:
        helper = open(os.path.dirname(__file__) + "/helper.js")
        return 200, helper.read()
    except Exception as e:
        print(e)
        return "404 Not Found", "Not Found"


class ServerEvent(Enum):
    on_response = "on_response"
    on_request = "on_request"
    on_render = "on_render"
    path_registered = "path_registered"
    new_session = "new_session"


class Server:
    """
    HTTP server handling routing and session management.
    """

    def __init__(self, adapter=ASGI):
        self.adapter = adapter(self.handle_request)
        # rewrite __call__ to expose the correct func signature
        self.__call__ = self.adapter
        self.routes = {}
        self.sessions: SessionManager = SessionManager()
        self._hooks: dict[ServerEvent, list[Callable[..., None]]] = {
            event: [] for event in ServerEvent
        }
        self.add_path("/_engine/helper.js", return_helper)
        self.registry_hook(ServerEvent.on_response, insert_helper_script)

    def __call__(self, *args, **kwargs):
        return self.adapter(*args, **kwargs)

    def registry_hook(self, event: ServerEvent, callback: Callable[..., None]):
        if callback in self._hooks:
            return

        event_hooks = self._hooks.get(event)
        if event_hooks is None:
            raise ServerError("Event dont exist")
        event_hooks.append(callback)

    def __call_hook__(self, event: ServerEvent, *payload):
        events = self._hooks.get(event)
        if events is None:
            return
        for callback in events:
            callback(*payload)

    def route(self, path):
        """Registers a function as a handler for a given route pattern."""

        def decorator(func):
            self.add_path(path, func)
            return func

        return decorator

    def add_path(self, path, func):
        """Manually adds a route-handler mapping."""

        path_regex = path_to_regex(path)
        self.__call_hook__(ServerEvent.path_registered, path, path_regex, func)
        self.routes[path_regex] = func

    def __handle_session__(self, cookies: dict, is_ssl: bool):
        header_session_cookie = None
        session_id = cookies.get(COOKIE_NAME)
        if session_id is None or not self.sessions.exist(session_id):
            session_id = self.sessions.create()
        secure = "; Secure" if is_ssl else ""
        header_session_cookie = (
            "Set-Cookie",
            (
                f"{COOKIE_NAME}={session_id}; "
                "HttpOnly; "
                "SameSite=Lax; "
                "Path=/; "
                f"Max-Age={self.sessions.max_ttl}"
                f"{secure}"
            ),
        )
        # self.__call_hook__(
        #     ServerEvent.new_session, session_id, self.sessions[session_id]
        # )

        return self.sessions.get(session_id), header_session_cookie

    def __process_response__(self, response) -> Response:
        res_code = Status.Ok
        res_headers = Headers()
        if isinstance(response, tuple):
            if len(response) == 3:
                res_code, headers, res_body = response
                res_headers = Headers(headers)

            elif len(response) == 2:
                res_code, res_body = response
            else:
                res_body = response[0]
        else:
            res_body = response

        self.__call_hook__(ServerEvent.on_response, res_code, res_body, res_headers)
        content_type = "text/plain"
        if isinstance(res_body, Component):
            content_type = "text/html"
            self.__call_hook__(ServerEvent.on_render, res_body)
            renderer = HTMLRenderer()
            res_body = renderer.render(res_body)
        elif isinstance(res_body, dict) or isinstance(res_body, list):
            content_type = "application/json"
            res_body = json.dumps(res_body)
        elif inspect.iscoroutine(res_body):
            frame = res_body.cr_frame
            location = (
                SourceLocation(file=frame.f_code.co_filename, line=frame.f_lineno)
                if frame
                else None
            )
            raise RenderError(  # TODO: implement Error class
                "Component returned a coroutine — did you forget 'await'?",
                f"  handler returned: {res_body.__name__}\n"
                f"  change 'return {res_body.__name__}()' to 'return await {res_body.__name__}()'",
                location=location,
            )

        res_headers.add("Content-Type", content_type)
        return Response(res_code, res_headers, res_body)

    async def handle_request(self, request: Request) -> Response:
        handler_and_match = match_path(self.routes, request.path)
        reset = init_render_ctx()
        self.__call_hook__(ServerEvent.on_request, request)
        if handler_and_match is None:
            return Response(
                Status.NotFound, [("Content-Type", "text/plain")], "Not Found"
            )

        params, handler = handler_and_match
        params["req"] = request
        _cookies = request.headers.get("COOKIE") or ""
        cookies = {
            k.strip(): v.strip()
            for k, v in (c.split("=", 1) for c in _cookies.split(";") if "=" in c)
        }
        session, session_header = self.__handle_session__(cookies, request.is_ssl)
        assert session is not None
        params["session"] = session.data
        params["cookies"] = cookies
        sig = inspect.signature(handler)
        params = {k: v for k, v in params.items() if k in sig.parameters}
        try:
            if inspect.iscoroutinefunction(handler):
                response = await handler(**params)
            else:
                # copy_context so the render context (a ContextVar) set by
                # init_render_ctx is visible inside the executor thread;
                # otherwise use_state()/@js registrations are silently lost
                context = contextvars.copy_context()
                response = await asyncio.get_event_loop().run_in_executor(
                    None, functools.partial(context.run, handler, **params)
                )

            response = self.__process_response__(response)
        finally:
            reset()

        if session_header is not None:
            response.headers.add(session_header[0], session_header[1])
        return response

    def serve(self, payload: str | Component):
        pass

from ..Elements import Component, script
from ..Server.Server import Server, ServerEvent


def enable_reactivity(server: Server):
    helper_script = script(src="_engine/helper.js")

    def event_handler(res_code, res_body, res_headers):
        if isinstance(res_body, Component):
            res_body.prepend(helper_script)

    server.registry_hook(ServerEvent.on_response, event_handler)

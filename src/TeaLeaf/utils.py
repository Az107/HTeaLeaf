from TeaLeaf.Html.Component import Component
from TeaLeaf.Html.Elements import script
from TeaLeaf.Server.Server import Server, ServerEvent
def redirect(path: str):
    return 302, [("Location", path)], ""


def enable_reactivity(server: Server):
    helper_script = script(src="_engine/helper.js")

    def event_handler(res_code, res_body, res_headers):
        if isinstance(res_body, Component):
            res_body.append(helper_script)

    server.registry_hook(ServerEvent.on_response, event_handler)

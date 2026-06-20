from ..Elements import Component, script




def insert_helper_script(res_code, res_body, res_headers):
    helper_script = script(src="_engine/helper.js")
    if isinstance(res_body, Component):
        res_body.prepend(helper_script)

# def enable_reactivity(server: Server):
#     helper_script = script(src="_engine/helper.js")

#     def event_handler(res_code, res_body, res_headers):


#     server.registry_hook(ServerEvent.on_response, event_handler)

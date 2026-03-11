from ..Magic.jslib.JSDO import JSDO

# class localState():
#     def __init__(self, init_state):
#         self.do = JSDO("LocalState",init_state)

#     def

#     def js(self):
#         return self.do.js()

#     def get(self):
#         return self.do.get()

#     def set(self, data):
#         return self.do.set(data)



def use_state(init_state):
    return JSDO("LocalState",init_state)

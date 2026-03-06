import json
import re
from typing import Any
from uuid import uuid4

from ..Html.Elements import script
from ..Html.JSCode import JSCode


class JSDO:
    def __init__(self, object_name: str, arg: Any):
        # js_file = os.path.dirname(__file__) + "/Store.js"
        self.obj_name = f"{object_name.lower()}_{str(uuid4())[:5]}"
        self.store_js = f"const {self.obj_name} = new {object_name}({json.dumps(arg)}); {self.obj_name}.id = '{self.obj_name}';"


    def __call__(self):
        return JSCode(self.obj_name)

    def __format_js__(self, func_name: str, *args) -> JSCode:

        def mark_js(obj):
            if isinstance(obj, JSCode):

                return f"__JS__:{obj.raw}"
            elif isinstance(obj, (list, tuple)):
                return [mark_js(o) for o in obj]
            elif isinstance(obj, dict):
                return {k: mark_js(v) for k, v in obj.items()}
            else:
                return obj

        marked = [mark_js(arg) for arg in args]
        payload = json.dumps(marked)
        payload = re.sub(r'"__JS__:(.*?)(?<!\\)"', lambda m: m.group(1).replace('\\"','"'), payload)
        base_js = f"""{self.obj_name}.{func_name}({payload[1:-1]})"""
        return JSCode(
            base_js
        )

    def new(self):
        return script(self.store_js)

    def get(self, *args):
        return self.__format_js__("get", *args)


    def set(self, *args):
        print("args:", args)
        return self.__format_js__("set", *args)

    def update(self, *args):
        return self.__format_js__("update", *args)

    def delete(self, *args):
        return self.__format_js__("delete", *args)



def Dom(query):
    return JSCode(f"""document.querySelector(`{query}`)""")


def Not(code: JSCode):
    return JSCode(f"!{code}")


def Set(code: JSCode, other: Any):
    return JSCode(f"{code.raw} = {other}")

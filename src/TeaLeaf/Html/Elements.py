import re
import sys
from typing import Any, List, Union

from TeaLeaf.Html.Component import Component, ComponentMeta
from TeaLeaf.Html.JSCode import JSCode


class html(Component, metaclass=ComponentMeta):
    pass


class head(Component, metaclass=ComponentMeta):
    pass

class header(Component, metaclass=ComponentMeta):
    pass

class link(Component, metaclass=ComponentMeta):
    pass

class script(Component):
    def __init__(self, *childs: Union[str, List[Any], "Component"] ,src=None):
        super().__init__("script", *childs)
        self.unsafe = True
        if src != None:
            self.attr(src=src)
            self.children = [""]
        else:
            funcs = []
            for child in childs:
                if type(child) is str:
                    pattern = r'\bfunction\s+([A-Za-z_$][\w$]*)\s*\('
                    funcs += re.findall(pattern, child)
            main_globals = sys.modules["__main__"].__dict__
            for func in funcs:
                main_globals[func] = JSCode(func)



class style(Component, metaclass=ComponentMeta):
    pass


class body(Component, metaclass=ComponentMeta):
    pass


class h1(Component, metaclass=ComponentMeta):
    pass


class h2(Component, metaclass=ComponentMeta):
    pass


class h3(Component, metaclass=ComponentMeta):
    pass


class div(Component, metaclass=ComponentMeta):
    pass

    def row(self):
        self.attr(style="display: flex; flex-direction: row")
        return self

    def column(self):
        self.attr(style="display: flex; flex-direction: column")
        return self


class button(Component, metaclass=ComponentMeta):

    def reactive(self,path,component_id):
        """
        Makes the button reactive by linking it to a FetchComponent.

        :param path: The URL to fetch new data from when clicked.
        :param component: The FetchComponent to be updated.
        """

        js = f"""fetchAndUpdate('{path}','{{}}','{component_id}')"""
        self.attr(onclick=js)
        return self



class label(Component, metaclass=ComponentMeta):
    pass

class checkbox(Component):
    def __init__(self,checked = False, *childs):
        super().__init__("input", *childs)
        self.attr(type="checkbox")
        if checked:
            self.attr(checked="True")

class textInput(Component):
    def __init__(self, *childs):
        super().__init__("input", *childs)

class submit(Component):
    def __init__(self, *childs):
        super().__init__("input", *childs)
        self.attr(type="submit")

class form(Component):
    def __init__(self, *childs):
        super().__init__("form", *childs)

    def action(self, action):
        self.attr(action=action)
        return self

    def method(self, method):
        self.attr(method=method)
        return self

from types import FunctionType
from typing import Any, List, Union

from ..JS import JSCode, JSFunction, js
from .Component import Component, ComponentMeta

__all__ = [
    "html",
    "head",
    "header",
    "link",
    "script",
    "body",
    "style",
    "div",
    "button",
    "select",
    "option",
    "label",
    "form",
    "checkbox",
    "textInput",
    "option",
    "submit",
]


class html(Component, metaclass=ComponentMeta):
    pass


class head(Component, metaclass=ComponentMeta):
    pass


class header(Component, metaclass=ComponentMeta):
    pass


class link(Component, metaclass=ComponentMeta):
    def __init__(self, *childs):
        super().__init__("link", *childs)


class script(Component):
    def __init__(
        self, *childs: Union[str, List[Any], "Component", JSFunction], src=None
    ):
        parsed_childs: Union[str, List[Any], "Component"] = []
        for child in childs:
            if type(child) is FunctionType:
                parsed_childs.append(js(child))
            elif type(child) is JSFunction:
                parsed_childs.append(child)
            else:
                parsed_childs.append(child)
        super().__init__("script", *parsed_childs)
        self.unsafe = True
        if src is not None:
            self.attr(src=src)
            self.children = [""]
        # else:


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
    def reactive(self, path, component_id):
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
    def __init__(self, checked=False, *childs):
        super().__init__("input", *childs)
        self.attr(type="checkbox")
        if checked:
            self.attr(checked="True")


class textInput(Component):
    def __init__(self, *childs):
        super().__init__("input", *childs)


class select(Component):
    def __init__(self, items: List[str]):
        super().__init__("select")
        for item in items:
            self.append(option(item))


class option(Component):
    def __init__(self, value):
        super().__init__("option", value)
        self.attr(value=value)


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


def tl_if(condition: JSCode | str | bool, *childs):
    if isinstance(condition, str):
        condition = JSCode(condition)

    return div(*childs).attr(style=f"display: {condition};")

import hashlib
import json
from typing import Any, List, Union

from ..JS import JSCode


class Component:
    """
    Represents an HTML component with attributes, children, and optional inline styles.
    This class allows constructing HTML elements programmatically and managing CSS styles.
    """

    def __init__(
        self, name, *childs: Union[str, List[Any], "Component", "JSCode"]
    ) -> None:
        """
        Initializes a new Component instance.

        :param name: The tag name of the HTML element.
        :param childs: Optional children elements, which can be strings, lists, or other Component instances.
        """

        self.styles: str | None = None
        self.name = name
        self.children: list[Component | str | list | JSCode] = list(childs)
        self.attributes: dict[str, str | None] = dict()
        self._id: str = self._generate_id()

    def _generate_id(self) -> str:
        """Genera un ID determinista basado en el contenido del componente."""
        content = {
            "name": self.name,
            "children": [
                child._id if isinstance(child, Component) else str(child)
                for child in self.children
            ],
        }
        raw = json.dumps(content, sort_keys=True)
        hash_str = hashlib.md5(raw.encode()).hexdigest()[:12]
        return f"tl-{hash_str}"

    def id(self, id: str):
        """
        Sets the ID of the component and adds it as an attribute.

        :param id: The ID to assign.
        :return: The component instance (for method chaining).
        """

        self._id = id
        return self.attr(id=id)

    def classes(self, classes):
        """
        Adds a CSS class attribute to the component.

        :param classes: CSS class names (space-separated).
        :return: The component instance (for method chaining).
        """

        self.attributes["class"] = classes
        return self

    def style(self, path: str | None = None, inline: bool = False, **attr):
        """
        Adds inline styles to the component.

        :param path: Optional path to an external CSS file.
        :param attr: CSS properties to apply (e.g., color="red", margin="10px").
        :return: The component instance (for method chaining).
        """
        if inline:
            self.attributes["style"] = " ".join(
                f"{k.replace('_', '-')}:{v};" for k, v in attr.items()
            )
        else:
            self.styles = (self.styles or "") + f"#{self._id} {{\n"
            self.styles += "\n".join(
                f"  {k.replace('_', '-')}: {v};" for k, v in attr.items()
            )
            self.styles += "\n}\n"

            if path:
                with open(path, "r") as f:
                    self.styles += f.read()
        return self

    def attr(self, *args, **attr):
        """
        Adds custom attributes to the component.

        :param attr: Dictionary of attribute names and values.
        :return: The component instance (for method chaining).
        """

        for arg in args:
            self.attributes[arg] = None

        for k in attr:
            # if type(attr[k]) is str:
            value = attr[k]
            # if isinstance(value, JSCode):
            #     value = f"{{{{{str(value)}}}}}"
            self.attributes[k] = value
            # elif type(attr[k]) is FunctionType:
            #     py_f = inspect.getsource(attr[k])
            #     self.attributes[k] = f"""() => pyodide.runPython(`{py_f}`)"""

        return self

    def append(self, child: Union[str, "Component", list]):
        """
        Appends a child element to the component.

        :param child: A Component, string, or list of elements.
        :return: The component instance (for method chaining).
        """

        self.children.append(child)
        return self

    def prepend(self, child: Union[str, "Component", list]):
        """
        Prepends a child element to the component.

        :param child: A Component, string, or list of elements.
        :return: The component instance (for method chaining).
        """

        self.children.insert(0, child)
        return self


class ComponentMeta(type):
    def __new__(cls, name, bases, dct):
        if name not in ("Component", "ComponentMeta"):

            def init(self, *childs):
                super(self.__class__, self).__init__(name, *childs)

            dct["__init__"] = init
        return super().__new__(cls, name, bases, dct)

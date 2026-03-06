import json
import os
import uuid
from typing import Any

from ..Html.Component import Component
from ..Html.Elements import div, script


class FetchComponent(Component):
    """
    A component that fetches data from a given URL and updates its content dynamically.
    """

    def __init__(self, url, body: str | dict | None = None) -> None:
        """
        Initializes a FetchComponent that loads content asynchronously.

        :param url: The URL to fetch data from.
        :param body: Optional request body for POST requests.
        """

        self._reid = new_id()
        placeholder = div("Loading...").id(self._reid)
        super().__init__("div", placeholder)
        # Configuración de la petición
        config = {"method": "POST" if body is not None else "GET", "body": body }
        # Serializar la configuración en JSON para JS
        _js_file = os.path.dirname(__file__) + "/MagicComponent.js"
        url = json.dumps(url)
        config_js = json.dumps(config)
        _id = json.dumps(placeholder._id)
        js: str = f"fetchAndUpdate({url},{config_js},{placeholder._id})"

        self.append(script(js))

    def reid(self):
        """
        Returns the reactive ID of the component.
        """

        return self._reid

class rButton(Component):
    """
    A reactive button that triggers updates on FetchComponents.
    """

    def __init__(self, *childs):
        """
        Initializes an rButton.

        :param childs: The child elements (text or components) inside the button.
        """
        super().__init__("button", *childs)

    def reactive(self,path,component: FetchComponent):
        """
        Makes the button reactive by linking it to a FetchComponent.

        :param path: The URL to fetch new data from when clicked.
        :param component: The FetchComponent to be updated.
        """

        #config = {"method": "GET"}
        if not hasattr(component, "reid"):
            raise Exception("component is not reactive")
        id = component.reid()
        # Serializar la configuración en JSON para JS
        #config_js = json.dumps(config)
        js = f"""fetchAndUpdate('{path}','{{}}','{id}')"""
        self.attr(onclick=js)
        return self

    #def refresh(self, path)

class HydratedComponent(Component):
    """
    WIP🚧
    A component that supports server-side hydration for dynamic updates.
    """

    def __init__(self, *childs):
        """
        Initializes a HydratedComponent.

        :param childs: The child elements inside the component.
        """

        pass


class PoolComponent(Component):
    """
    WIP🚧
    A component that periodically fetches data from a URL and updates itself.
    """

    def __init__(self, child: Component, url: str, interval: int = 5000):
        """
        Initializes a PoolComponent.

        :param child: The component to be updated.
        :param url: The URL from which new data will be fetched.
        :param interval: The time interval (in milliseconds) for polling updates. Default is 5000ms.
        """
        super().__init__("div", child)
        js = f"""
        setInterval(() => fetchAndUpdate('{url}', '{{}}', '{child._id}'), {interval});
        """
        self.append(script(js))


def new_id():
    """
    Generates a new unique identifier for reactive components.
    """
    return "tlmg" + str(uuid.uuid4()).split("-")[0]


def to_js_type(data: Any) -> str:
    return json.dumps(data)

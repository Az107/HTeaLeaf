import copy
import json
from typing import Any
from uuid import uuid4

from ..Elements import Component, div, script
from ..JS import JSCode
from ..Server.Http import Request
from ..Server.Server import Server, ServerEvent, Session


class SuperStore:
    _instance = None
    _initialized = False

    def __new__(cls, server=None):
        if cls._instance is None:
            cls._instance = super(SuperStore, cls).__new__(cls)
        return cls._instance

    def inject_stores(self, res_code, res_body, res_headers):
        if isinstance(res_body, Component):
            for store_id in self.stores:
                store = self.stores[store_id]
                res_body.append(
                    script(f'const {store._js} = new Store("{store._id}");')
                )

    def __init__(self, server: Server | None = None):
        if not self._initialized:
            self.stores: dict[str, Store | AuthStore] = {}
            self._initialized = True
            if server:
                server.add_path("/api/_store/{api_id}/*", self.process)
                server.registry_hook(ServerEvent.on_response, self.inject_stores)

            self._initialized = True

    def len(self):
        return len(self.stores)

    def add(self, id, store: "Store | AuthStore"):
        self.stores[id] = store

    def process(self, session: Session, req: Request, api_id):
        path = req.path.removeprefix(f"/api/_store/{api_id}/")

        store = self.stores.get(api_id)
        if store is None:
            return "Not found"

        if isinstance(store, AuthStore):
            store = store.auth(session)

        if store is None:
            return "404 Not Found", "Not found"

        if req.method == "GET":
            return json.dumps(store.read(path))
        elif req.method == "POST":
            data = req.json()
            text = req.text()
            if data is None:
                data = text
            return json.dumps(store.create(path, data))
        elif req.method == "DELETE":
            return json.dumps(store.delete(path))
        elif req.method == "PATCH":
            data = req.json()
            text = req.text()
            if data is None:
                data = text
            return json.dumps(store.update(path, data))
        else:
            return "404 Not Found", "Not found"


class Store:
    def __init__(self, default={}, subscribe=True, id=str(uuid4())):
        self._id = id
        self.data = copy.copy(default)
        self._js = JSCode(f"store_{self._id[:8]}")
        if subscribe:
            SuperStore().add(self._id, self)

    def __get_pointer__(self, path):
        pointer = self.data
        for item in path:
            # if not isinstance(pointer, Iterable):
            #     return None
            if type(pointer) is list:
                item = int(item)
                pointer = pointer[item]
            else:
                if item in pointer:
                    pointer = pointer[item]
                else:
                    return None
        return pointer

    def delete(self, path):
        path = path.split("/") if path != "" else []

        parent = self.__get_pointer__(path[:-1])
        if parent is None:
            return None
        item = path[-1]
        if type(parent) is list:
            del parent[int(item)]
            return True
        else:
            if item in parent:
                del parent[item]
                return True
            else:
                return False

    def update(self, path, data):
        path = path.split("/") if path != "" else []

        parent = self.__get_pointer__(path[:-1])
        item = path[-1]
        if parent is None:
            return None
        parent[item] = data

        return data

    def read(self, path: str) -> Any:
        path_list = path.split("/") if path != "" else []
        pointer = self.__get_pointer__(path_list)
        return pointer

    def react(self, path) -> Component:
        return div(self.read(path)).classes(f"{self._id}{id}_react")

    def create(self, path: str, data):
        path_list = path.split("/") if path != "" else []
        parent = self.__get_pointer__(path_list[:-1])
        if parent is None:
            return None
        item = path_list[-1]

        if item in parent:
            pointer = parent[item]
            if type(pointer) is dict:
                parent[item].update(data)
            elif type(pointer) is list:
                if not hasattr(data, "key"):
                    data["key"] = str(uuid4())
                pointer.append(data)
            else:
                return None

        else:
            parent[item] = data

        return parent


class AuthStore:
    def __init__(self, auth, default={}) -> None:
        self._id = str(uuid4())
        self.default = default
        self.data: dict[str, Store] = {}
        self.auth_func = auth
        self._js = JSCode(f"store_{self._id[:8]}")
        SuperStore().add(self._id, self)

    def auth(self, session: Session) -> Store:
        key = self.auth_func(session)
        if key not in self.data:
            self.data[key] = Store(
                default=copy.deepcopy(self.default), subscribe=False, id=self._id
            )
        return self.data[key]

    # Store methods to allow use in JS Functions
    # TODO: change error to raise Not Authenticated
    def set(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, *args, **kwargs):
        raise NotImplementedError()

    def delete(self, *args, **kwargs):
        raise NotImplementedError()

    def update(self, *args, **kwargs):
        raise NotImplementedError()

    def create(self, *args, **kwargs):
        raise NotImplementedError()

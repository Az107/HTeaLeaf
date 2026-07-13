import copy
import json
from typing import Any
from uuid import uuid4

from ..elements import Component, script
from ..js import JSCode
from ..server import SessionData
from ..server.http import Request
from ..server.server import Server, ServerEvent


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
                res_body.append(script(f'const {store.js} = new Store("{store._id}");'))

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

    def process(self, session: SessionData, req: Request, api_id):
        path = req.path.removeprefix(f"/api/_store/{api_id}/")

        store = self.stores.get(api_id)
        if store is None:
            return 404, "Not found"

        if isinstance(store, AuthStore):
            store = store.auth(session)

        if store is None:
            return 404, "Not found"

        if req.method == "GET":
            return json.dumps(store.read(path))
        elif req.method == "POST":
            data = req.json()
            text = req.text()
            if data is None:
                data = text
            try:
                return json.dumps(store.create(path, data))
            except BadRequestError as e:
                return 400, str(e)
        elif req.method == "DELETE":
            return json.dumps(store.delete(path))
        elif req.method == "PATCH":
            data = req.json()
            text = req.text()
            if data is None:
                data = text
            return json.dumps(store.update(path, data))
        else:
            return 404, "Not found"


class Store:
    def __init__(self, default={}, subscribe=True, id=None):
        self._id = id if id is not None else str(uuid4())
        self.data = copy.copy(default)
        self.js = JSCode(f"store_{self._id[:8]}")
        if subscribe:
            SuperStore().add(self._id, self)

    def __get_pointer__(self, path) -> tuple[Any, str | int | None]:
        pointer = self.data
        path_parent = path[:-1]
        for item in path_parent:
            # if not isinstance(pointer, Iterable):
            #     return None
            if isinstance(pointer, list):
                item = int(item)
                pointer = pointer[item]
            elif isinstance(pointer, dict):
                if item in pointer:
                    pointer = pointer[item]
                else:
                    raise BadRequestError(f"Item {item} not found in {pointer}")

            else:
                raise BadRequestError(f"Item {item} not found in {pointer}")

        if len(path) == 0:
            return pointer, None
        item = path[-1]
        if isinstance(pointer, list):
            item = int(item)
        elif isinstance(pointer, dict):
            if item not in pointer:
                raise BadRequestError(f"Item {item} not found in {pointer}")
        return pointer, item

    def delete(self, path):
        path = path.split("/") if path != "" else []

        parent, item = self.__get_pointer__(path)
        if item is not None:
            del parent[item]
        else:
            raise NotFoundError(f"Item {path} not found")

    def update(self, path, data):
        path = path.split("/") if path != "" else []

        parent, item = self.__get_pointer__(path)
        if parent is None:
            return None
        if item is None:
            raise NotFoundError(f"Item {path} not found")

        parent[item] = data

        return parent[item]

    def read(self, path: str) -> Any:
        path_list = path.split("/") if path != "" else []
        pointer, item = self.__get_pointer__(path_list)
        if item is None:
            return pointer
        return pointer[item]

    def create(self, path: str, data):
        path_list = path.split("/") if path != "" else []
        parent, item = self.__get_pointer__(path_list)
        print(parent, item, data)

        if item is None:
            if isinstance(parent, dict):
                parent.update(data)
            elif isinstance(parent, list):
                parent.append(data)
            else:
                raise BadRequestError(
                    "Cannot create at root: existing value is not a dict or list"
                )
            return parent
        if isinstance(parent[item], dict):
            parent[item].update(data)
        elif isinstance(parent[item], list):
            if isinstance(data, dict) and "key" not in data:
                data["key"] = str(uuid4())
            parent[item].append(data)
        else:
            raise BadRequestError(
                f"Cannot create at '{item}': existing value is not a dict or list"
            )

        return parent

    # Store methods to allow use in JS Functions
    # TODO: change error to raise Not Authenticated
    def set(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, *args, **kwargs):
        raise NotImplementedError()


class AuthStore:
    def __init__(self, auth, default={}) -> None:
        self._id = str(uuid4())
        self.default = default
        self.data: dict[str, Store] = {}
        self.auth_func = auth
        self.js = JSCode(f"store_{self._id[:8]}")
        SuperStore().add(self._id, self)

    def auth(self, session: SessionData) -> Store:
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


class BadRequestError(Exception):
    pass


class NotFoundError(Exception):
    pass

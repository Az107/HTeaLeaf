BANNED_HEADERS = []

class Headers():
    def __init__(self, data: list[tuple[str,str]] | dict[str,str] = []):
        self._data: dict[str, str] = {}
        for k in data:
            if isinstance(k, str) and isinstance(data, dict):
                self._data[k] = data[k]
            else:
                self._data[k[0]] = k[1]

    def __iter__(self):
        for k in self._data:
            yield (k, self._data[k])


    def __getitem__(self, key: str):
        return self._data.get(key.lower())


    def __setitem__(self, name: str, value: str) -> None:
        if name.lower() in self._data:
            if name.lower() in BANNED_HEADERS:
                raise Exception("Invalid duplicated header")
            self._data[name] += "; " + value
        else:
            self._data[name] = value

    def add(self, key: str, value: str):
        self._data[key] = value

    def get(self, key: str):
        for k in self._data:
            if k.lower() == key.lower():
                return self._data.get(k)
        return None


    def __contains__(self, item):
        return item.lower() in self._data

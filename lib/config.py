import json
import typing

class Config:
    def __init__(self, filename: str):
        self._filename = filename

        try:
            file = open(filename)
        except FileNotFoundError:
            self.config = {}
            return
            
        self.config = json.loads(file.read())
        file.close()

    def get_int(self, key: str, default: int) -> int:
        value = self.config.get(key)
        if value == None:
            value = default
        return value

    def get_bool(self, key: str, default: bool) -> bool:
        value = self.config.get(key)
        if value == None:
            value = default
        return value

    def set(self, key: str, value):
        self.config[key] = value
        file = open(self._filename, "w")
        file.write(json.dumps(self.config))
        file.close()

from enum import Enum

from .HttpHeader import Headers


class HttpResponse:
    status: "HttpStatus"
    headers: Headers
    body: str | bytes

    def __init__(self, status: "HttpStatus" | tuple[int,str] | int, headers: Headers | list[tuple[str,str]], body: str | bytes, / ):
        if isinstance(status, HttpStatus):
            self.status = status
        elif isinstance(status,tuple):
            self.status = HttpStatus.custom(status[0], status[1])
        elif isinstance(status, int):
            self.status = HttpStatus.from_int(status)
        else:
            raise Exception(f"invalid status: {status}")

        if isinstance(headers,Headers):
            self.headers = headers
        elif isinstance(headers,list):
            self.headers = Headers(headers)
        else:
            raise Exception("invalid headers")

        self.body = body



class HttpStatus(Enum):
    Ok = 200, "Ok"
    Created = 201, "Created"
    NoContent = 204, "No Content"

    Found = 302, "Found"

    BadRequest = 400, "Bad Request"
    Unauthorized = 401, "Unauthorized"
    Forbidden = 403, "Forbiden"
    NotFound = 404, "Not Found"
    Conflict = 409, "Conflict"

    InternalServerError = 500, "Internal Server Error"
    NotImplemented = 501, "Not Implemented"
    BadGateway = 502, "Bad Gateway"
    ServiceUnavailable = 503, "Service Unavailable"
    _Other = None, None # Placeholder


    @classmethod
    def custom(cls, code, message):
        instance = cls._Other
        instance._value_ = code, message
        return instance

    @classmethod
    def from_int(cls, code: int):
        for status in cls:
            if status.value[0] == code:
                return status
        raise Exception(f"Invalid status {code}")


    def to_int(self) -> int:
        if self.value[0] is None:
            raise Exception(f"Invalid status {self.value}")
        return self.value[0]


    def to_str(self) -> str:
        if self.value is None:
            raise Exception(f"Invalid status {self}")
        return f"{self.value[0]} {self.value[1]}"

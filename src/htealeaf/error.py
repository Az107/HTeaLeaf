class HTeaLeafError(Exception):
    def __init__(self, message: str, hint: str):
        self.message = message
        self.hint = hint
        super().__init__(message)

    def __str__(self):
        return self.message


# Subclasses per subsystem
class TranspilerError(HTeaLeafError):
    pass


class RenderError(HTeaLeafError):
    pass


class StateError(HTeaLeafError):
    pass


class RoutingError(HTeaLeafError):
    pass

import inspect
import linecache
import sys
import sysconfig
from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceLocation:
    file: str
    line: int
    column: Optional[int] = None

    def snippet(self) -> Optional[str]:
        text = linecache.getline(self.file, self.line)
        return text.rstrip("\n") if text else None


def _htealeaf_excepthook(exc_type, exc_value, tb):
    if isinstance(exc_value, HTeaLeafError):
        print(exc_value.format(), file=sys.stderr)
    else:
        sys.__excepthook__(exc_type, exc_value, tb)


def enable_friendly_errors():
    """Opt-in: reemplaza el traceback completo por el formato friendly
    para errores HTeaLeafError. Pensado para dev, no para producción."""
    sys.excepthook = _htealeaf_excepthook


_STDLIB_DIR = sysconfig.get_path("stdlib")
_PLATSTDLIB_DIR = sysconfig.get_path("platstdlib")


def _is_user_frame(filename: str) -> bool:
    if "htealeaf" in filename:
        return False
    if "site-packages" in filename or "dist-packages" in filename:
        return False
    if filename.startswith(_STDLIB_DIR) or filename.startswith(_PLATSTDLIB_DIR):
        return False
    return True


def _find_user_frame():
    for frame_info in inspect.stack():
        if _is_user_frame(frame_info.filename):
            return SourceLocation(file=frame_info.filename, line=frame_info.lineno)
    return None


class HTeaLeafError(Exception):
    """Base error for all HTeaLeaf-raised exceptions."""

    def __init__(
        self,
        message: str,
        hint: Optional[str] = None,
        location: Optional[SourceLocation] = None,
    ):
        self.message = message
        self.hint = hint
        self.location = location or _find_user_frame()
        super().__init__(message)

    def __str__(self):
        return self.format()

    def format(self) -> str:
        lines = ["\n\n"]
        lines.append(f"{self.message}")

        if self.location:
            lines.append(f"  --> {self.location.file}:{self.location.line}")
            snippet = self.location.snippet()
            if snippet:
                lines.append("    |")
                lines.append(f"{self.location.line:>3} | {snippet.strip()}")
                lines.append("    |")

        if self.hint:
            lines.append(f"hint: {self.hint}")
        return "\n".join(lines)


# --- Subclases por subsistema ---


class RenderError(HTeaLeafError):
    pass


class TranspilerError(HTeaLeafError):
    pass


class StateError(HTeaLeafError):
    pass


class RoutingError(HTeaLeafError):
    pass


class ServerError(HTeaLeafError):
    def __init__(
        self,
        message: str,
        hint: Optional[str] = None,
        location: Optional[SourceLocation] = None,
    ):
        self.message = message
        self.hint = hint
        self.location = None
        super().__init__(message)


from dataclasses import dataclass
from typing import Any

from .JSCode import JSCode


@dataclass
class document(JSCode):
    def __init__(self):
        super().__init__("document")

    getElementById: JSCode
    getElementByClassName: JSCode
    getElementsByTagName: JSCode
    querySelector: JSCode
    querySelectorAll: JSCode
    createElement: JSCode


def Not(code: JSCode):
    return JSCode(f"!{code}")

def Set(code: JSCode, other: Any):
    return JSCode(f"{code.raw} = {other}")

def Eq(code: JSCode, other: Any):
    return JSCode(f"{code.raw} == {other}")

def Ne(code: JSCode, other: Any):
    return JSCode(f"{code.raw} != {other}")

def Gt(code: JSCode, other: Any):
    return JSCode(f"{code.raw} > {other}")

def Lt(code: JSCode, other: Any):
    return JSCode(f"{code.raw} < {other}")



console = JSCode("console")
window = JSCode("window")
alert = JSCode("alert")
event = JSCode("event")

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from HTeaLeaf.JS.JSCode import JSCode

from ..Component import Component

T = TypeVar("T")


class Renderer(ABC, Generic[T]):
    def __init__(self) -> None:
        super().__init__()
        self.css = {}

    @abstractmethod
    def __render_component__(self, cmpt: Component) -> T: ...

    @abstractmethod
    def render(
        self,
        cmpt: Component | list | str | JSCode | Any,
        subrender=False,
    ) -> T: ...

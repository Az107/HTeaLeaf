from typing import Any
import inspect
from HTeaLeaf.JS.JSCode import JSCode

from ..Component import Component
from ..Elements import script
from .render_context import get_render_ctx
from .renderer import Renderer


class HTMLRenderer(Renderer[str]):
    def __render_component__(self, cmpt: Component) -> str:
        """
        Builds and returns the full HTML including inline CSS inside a <style> tag.

        :return: A complete HTML string with embedded CSS.
        """

        def __build_attr__(cmpt: Component) -> str:
            return " " + " ".join(
                f"{k}='{v}'" if v is not None else f"{k}"
                for k, v in cmpt.attributes.items()
            )

        if len(cmpt.children) == 0:
            result = f"<{cmpt.name}{__build_attr__(cmpt)}/>\n"
        else:
            inner_result = self.render(cmpt.children, subrender=True)
            result = f"<{cmpt.name}{__build_attr__(cmpt)}>\n"
            if cmpt.styles is not None:
                self.css[cmpt.id] = cmpt.styles
            result += inner_result
            result += f"</{cmpt.name}>\n"
        return result

    def render(
        self,
        cmpt: Component | list | str | JSCode | Any,
        subrender=False,
    ) -> str:

        if inspect.iscoroutine(cmpt):
            raise Exception(
                "Component returned a coroutine — did you forget 'await'?\n"
                f"  handler returned: {cmpt.__name__}\n"
                f"  hint: change 'return {cmpt.__name__}()' to 'return await {cmpt.__name__}()'"
            )

        if not subrender:
            ctx = get_render_ctx()
            if ctx is not None and isinstance(cmpt, Component):
                node = cmpt.get_child("head") or cmpt
                for fn in ctx.js_functions:
                    node.append(script(fn))
                for fn in ctx.state_initializers:
                    node.append(script(fn))

        html_parts = []
        if isinstance(cmpt, str):
            html_parts.append(f"{cmpt}")
        elif isinstance(cmpt, list):
            for child in cmpt:
                html = self.render(child, subrender=True)
                html_parts.append(html)
        elif isinstance(cmpt, Component):
            html = self.__render_component__(cmpt)
            html_parts.append(html)
        elif isinstance(cmpt, JSCode):
            # JSCode outside of an attribute should be a special tag {{jscode_name}}
            html_parts.append(f"{{{{{cmpt.raw}}}}}")
        else:
            try:
                html_parts.append(str(cmpt))
            except Exception:
                raise Exception("Can't render item")

        return "".join(html_parts)

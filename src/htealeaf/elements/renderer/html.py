import html
import inspect
from typing import Any

from htealeaf.error import RenderError, SourceLocation
from htealeaf.js.jscode import JSCode

from ..component import Component
from ..elements import script
from .render_context import get_render_ctx
from .renderer import Renderer

# Elements whose text content is CDATA in HTML and must not be escaped,
# otherwise inline JS/CSS (e.g. injected @js functions) would break.
RAW_TEXT_TAGS = {"script", "style"}


class HTMLRenderer(Renderer[str]):
    def __render_component__(self, cmpt: Component) -> str:
        """
        Builds and returns the full HTML including inline CSS inside a <style> tag.

        :return: A complete HTML string with embedded CSS.
        """

        def __build_attr__(cmpt: Component) -> str:
            return " " + " ".join(
                f"{k}='{html.escape(str(v), quote=False)}'" if v is not None else f"{k}"
                for k, v in cmpt.attributes.items()
            )

        if len(cmpt.children) == 0:
            result = f"<{cmpt.name}{__build_attr__(cmpt)}/>\n"
        else:
            inner_result = self.render(
                cmpt.children, subrender=True, raw_text=cmpt.name in RAW_TEXT_TAGS
            )
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
        raw_text=False,
    ) -> str:

        if inspect.iscoroutine(cmpt):
            raise RenderError(  # TODO: implement Error class
                "Component returned a coroutine — did you forget 'await'?",
                f"  handler returned: {cmpt.__name__}\n"
                f"  hint: change 'return {cmpt.__name__}()' to 'return await {cmpt.__name__}()'",
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
            html_parts.append(cmpt if raw_text else html.escape(cmpt))
        elif isinstance(cmpt, list):
            for child in cmpt:
                rendered = self.render(child, subrender=True, raw_text=raw_text)
                html_parts.append(rendered)
        elif isinstance(cmpt, Component):
            rendered = self.__render_component__(cmpt)
            html_parts.append(rendered)
        elif isinstance(cmpt, JSCode):
            # JSCode outside of an attribute should be a special tag {{jscode_name}}
            html_parts.append(f"{{{{{cmpt.raw}}}}}")
        else:
            try:
                html_parts.append(str(cmpt))
            except Exception:
                import sys

                raise RenderError(
                    "Can't render item",
                    location=SourceLocation(
                        file=sys._getframe().f_code.co_filename,
                        line=sys._getframe().f_lineno,
                    ),
                )

        return "".join(html_parts)

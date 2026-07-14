from htealeaf.elements import Component
from htealeaf.elements.renderer.html import HTMLRenderer
from htealeaf.js import JSCode

STATIC_COMPONENT = Component("div", "Hello, World!")


EXPECTED_OUTPUT = "<div >Hello, World!</div>"


def test_render():
    renderer = HTMLRenderer()
    result = renderer.render(STATIC_COMPONENT)
    assert isinstance(result, str)
    assert result == EXPECTED_OUTPUT


def test_paragraph():
    renderer = HTMLRenderer()
    paragraph = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Duis aute irure dolor in reprehenderit in voluptate velit
    esse cillum dolore eu fugiat nulla pariatur.
    """
    result = renderer.render(Component("p", paragraph))
    assert isinstance(result, str)
    assert result == "<p >" + paragraph + "</p>"


def test_attributes():
    renderer = HTMLRenderer()
    result = renderer.render(Component("div", "Hello, World!").id("my-div"))
    result2 = renderer.render(Component("div", "Hello, World!").attr(id="my-div"))
    assert isinstance(result, str)
    assert result == result2
    assert result == "<div id='my-div'>Hello, World!</div>"


def test_malformed_attributes():
    render = HTMLRenderer()
    result = render.render(Component("div", "Hello, World!").attr(id="<my-div/>"))
    assert isinstance(result, str)
    assert result == "<div id='&lt;my-div/&gt;'>Hello, World!</div>"


def test_js_attributes():
    renderer = HTMLRenderer()
    console = JSCode("console")
    result = renderer.render(
        Component("div", "Hello, World!").attr(
            id="my-div", onsomething=console.log("test")
        )
    )
    assert isinstance(result, str)
    assert (
        result
        == "<div id='my-div' onsomething='console.log(\"test\")'>Hello, World!</div>"
    )

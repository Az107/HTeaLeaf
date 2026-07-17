from htealeaf.elements import Component

def test_component_stores_name():
    c = Component("div")
    assert c.name == "div"

def test_component_stores_children_as_list():
    c = Component("div", "hello", "world")
    assert c.children == ["hello", "world"]

def test_component_with_no_children_is_empty_list():
    c = Component("div")
    assert c.children == []

def test_component_accepts_nested_component_as_child():
    inner = Component("span", "hi")
    outer = Component("div", inner)
    assert outer.children == [inner]

def test_component_accepts_list_as_child():
    c = Component("ul", [Component("li", "a"), Component("li", "b")])
    assert len(c.children) == 1
    assert isinstance(c.children[0], list)


def test_attributes_starts_empty():
    assert Component("div").attributes == {}

def test_styles_starts_none():
    assert Component("div").styles is None

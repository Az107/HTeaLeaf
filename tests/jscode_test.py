from htealeaf.js import JSCode


def test_js_code():
    code = JSCode("")
    assert str(code) == ""


def test_js_code_with_string():
    code = JSCode("hello")
    assert str(code) == "hello"


def test_js_code_with_operators():
    code = JSCode("a") + JSCode("b")
    assert str(code) == "(a + b)"


def test_js_attributes():
    code = JSCode("a")
    assert str(code.b) == "a.b"
    assert str(code.b.c) == "a.b.c"


def test_js_code_call():
    code = JSCode("a")
    assert str(code.b.c()) == "a.b.c()"


def test_js_code_call_with_args():
    code = JSCode("a")
    assert str(code.b.c(1, 2, 3)) == "a.b.c(1,2,3)"
    assert str(code.b.c(1, 2, 3).d) == "a.b.c(1,2,3).d"
    assert str(code.b.c(1, 2, 3, "4").d) == 'a.b.c(1,2,3,"4").d'

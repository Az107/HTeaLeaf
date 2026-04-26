from HTeaLeaf.Elements import (
    body,
    button,
    checkbox,
    div,
    form,
    h1,
    h2,
    h3,
    head,
    header,
    html,
    link,
    script,
    submit,
    textInput,
)
from HTeaLeaf.JS import js
from HTeaLeaf.JS.common import alert, document, window
from HTeaLeaf.Server.Http import Request
from HTeaLeaf.Server.Server import Server, Session
from HTeaLeaf.Server.utils import redirect
from HTeaLeaf.State.HelperMidleware import enable_reactivity
from HTeaLeaf.State.LocalState import use_state
from HTeaLeaf.State.Store import AuthStore, Store, SuperStore


def auth_session(session: Session):
    if session.has("userName"):
        return session["userName"]
    return None


def init(app: Server):
    global cstore
    global todoStore

    enable_reactivity(app)
    SuperStore(app)
    cstore = Store({"counter": 1})
    todoStore = AuthStore(auth_session, {"todo": []})
    app.add_path("/health", health)
    app.add_path("/contar", counter)
    app.add_path("/hello/{name}", greet)
    app.add_path("/login", user)
    app.add_path("/example", userNav)
    app.add_path("/logout", logout)
    app.add_path("/", home)


mincss_url = (
    "https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css"
)
mincss = link().attr(rel="stylesheet", href=mincss_url)


def health(req: Request):
    return {
        "status": "ok",
        "method": req.method,
        "path": req.path,
        "body": str(req.json()),
    }


def counter():

    return div(
        button("-").attr(
            onclick=cstore._js.update(
                "counter", cstore.read("counter") - 1
            )  # TODO: remplace _js
        ),
        h3(cstore.react("counter")),
        button("+").attr(
            onclick=cstore._js.update("counter", cstore.read("counter") + 1)
        ),
    ).row()


def greet(name):
    return (
        200,
        [("potato-header", "yay")],
        f"Hello {name}",
    )


def LoginPage():
    return html(
        mincss,
        form(textInput().id("userName").attr(name="userName"), submit("Login"))
        .action("/login")
        .method("POST"),
    )


def user(session, req: Request):
    if session.has("userName"):
        return "Hello " + session.userName
    user = req.form()
    if user is None or "userName" not in user:
        return 401, LoginPage()
    else:
        session.userName = user["userName"]
        return redirect("/")


def userNav(req: Request):
    user = req.json()
    if user is None:
        name = ""
    else:
        name = user["name"]
    userCard = div(
        script("""
            console.log("loaded");
            """),
        div(f"Username {name}"),
        button("logout")
        .attr(onclick="alert('login out')")
        .style(backgroud_color="blue"),
    ).row()
    return userCard


def todoItem(id, task):

    return (
        div(
            checkbox(checked=task["done"]).attr(
                onchange=todoStore._js.update(f"todo/{id}/done", not task["done"])
            ),
            h2(task["value"]).style(text_overflow="ellipsis"),
            button("x")
            .classes("secondary")
            .attr(onclick=todoStore._js.delete(f"todo/{id}")),
        )
        .row()
        .classes("card")
    )


def logout(session):
    if session.has("userName"):
        del session["userName"]
    return redirect("/login")


def home(session, req: Request):
    if not session.has("userName"):
        return redirect("/login")

    modal_state = use_state("none")
    localCounter = use_state(0)

    @js
    def addTodoIfNotEmpty(inputId):
        val = document.getElementById(inputId).value
        if val.trim() != "":
            todoStore.set("todo", {"done": False, "value": val})
            document.getElementById(inputId).value = ""
        else:
            alert("empty task")

    @js
    def toggleModal():
        if modal_state.get() == "none":
            modal_state.set("block")
        else:
            modal_state.set("none")

    web = html(
        head(
            mincss,
        ),
        body(
            header(
                div(
                    h1("HTeaLeaf!").style(color="green"),
                    button(f"Welcome {session['userName']} {localCounter}").attr(
                        onclick=window.location.replace("/logout")
                    ),
                ).row()
            ),
            button("toggle modal").attr(onclick=toggleModal()),
            div("This is a modal: ", modal_state)
            .id("modal")
            .classes("card")
            .row()
            .style(inline=True, display=modal_state),
            div(
                button("-").attr(onclick=localCounter.set(localCounter.get() - 1)),
                localCounter,
                button("+").attr(onclick=localCounter.set(localCounter.get() + 1)),
            )
            .classes("card")
            .row(),
            div(
                counter(),
                div(
                    [
                        todoItem(idx, c)
                        for idx, c in enumerate(todoStore.auth(session).read("todo"))
                    ]
                ).style(padding="20px", height="200px", overflow_y="scroll"),
                div(
                    textInput().id("todo_item"),
                    button("Create").attr(onclick=addTodoIfNotEmpty("todo_item")),
                ).row(),
            ),
        ),
    )
    return web

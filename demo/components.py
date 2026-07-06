from htealeaf import AuthStore, Store, SuperStore, use_state
from htealeaf.elements import (
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
    style,
    submit,
    textInput,
)
from htealeaf.js import js
from htealeaf.js.common import alert, console, document, event, window
from htealeaf.server import Server
from htealeaf.server.http import Request
from htealeaf.server.utils import redirect


def auth_session(session):
    if session.has("userName"):
        return session["userName"]
    return None


def init(app: Server):
    global cstore
    global todoStore

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
            onclick=cstore.js.update("counter", cstore.read("counter") - 1)
        ),
        h3(cstore.read("counter")),
        button("+").attr(
            onclick=cstore.js.update("counter", cstore.read("counter") + 1)
        ),
    ).row()


def greet(name):
    return (
        200,
        [("potato-header", "yay")],
        f"Hello {name}",
    )


async def LoginPage():
    return html(
        mincss,
        form(textInput().id("userName").attr(name="userName"), submit("Login"))
        .action("/login")
        .method("POST"),
    )


async def user(session, req: Request):
    if session.has("userName"):
        return "Hello " + session["userName"]
    user = req.form()
    if user is None or "userName" not in user:
        return 401, await LoginPage()
    else:
        session["userName"] = user["userName"]
        return redirect("/")


async def userNav(req: Request):
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
                onchange=todoStore.js.update(f"todo/{id}/done", not task["done"])
            ),
            h2(task["value"]).style(text_overflow="ellipsis"),
            button("x")
            .classes("secondary")
            .attr(onclick=todoStore.js.delete(f"todo/{id}")),
        )
        .row()
        .classes("card")
    )


def logout(session):
    if session.has("userName"):
        del session["userName"]
    return redirect("/login")


async def home(session, req: Request):
    if not session.has("userName"):
        return redirect("/login")

    modal_state = use_state("none")
    modal_button_state = use_state("open")
    localCounter = use_state(0)
    user_title = use_state(f"Welcome {session['userName']}")

    @js
    def addTodoIfNotEmpty(inputId):
        val = document.getElementById(inputId).value
        if val.trim() != "":
            todoStore.set("todo", {"done": False, "value": val})
            document.getElementById(inputId).value = ""
        else:
            alert("empty task")

    @js
    def addOnKeyPress(e):
        console.log(e.key)
        if e.key == "Enter" or e.keyCode == 13:
            addTodoIfNotEmpty("todo_item")

    @js
    def toggleModal():
        if modal_state.get() == "none":
            modal_state.set("block")
            modal_button_state.set("close")
        else:
            modal_state.set("none")
            modal_button_state.set("open")

    web = html(
        head(
            mincss,
            style(
                {
                    "body": {"background-color": "teal"},
                    "#modal": {
                        "position": "fixed",
                        "z-index": "1",
                        "top": "20%",
                        "left": "20%",
                    },
                }
            ),
        ),
        body(
            header(
                div(
                    h1("HTeaLeaf!").style(color="teal"),
                    button(user_title).attr(
                        onclick=window.location.replace("/logout"),
                        onmouseover=user_title.set("logout"),
                        onmouseleave=user_title.set(f"Welcome {session['userName']}"),
                    ),
                )
                .row()
                .style(display="flex", align_items="center")
            ).style(
                margin="10px", border_radius="5px", shadow="0 0 10px rgba(0, 0, 0, 0.5)"
            ),
            div(
                button(f"{modal_button_state} modal").attr(onclick=toggleModal()),
                div(
                    div(
                        h3("Modal"),
                        button("X")
                        .attr(onclick=toggleModal())
                        .style(background_color="red", color="white", float="right"),
                    ).style(
                        display="flex",
                        align_items="center",
                        justify_content="space-between",
                        padding="0px",
                        width="100%",
                    ),
                    "This is a modal: ",
                    modal_state,
                    div(
                        button("-").attr(
                            onclick=localCounter.set(localCounter.get() - 1)
                        ),
                        localCounter,
                        button("+").attr(
                            onclick=localCounter.set(localCounter.get() + 1)
                        ),
                    ).row(),
                )
                .id("modal")
                .classes("card")
                .row()
                .style(inline=True, display=modal_state),
                div(
                    counter(),
                    div(
                        [
                            todoItem(idx, c)
                            for idx, c in enumerate(
                                todoStore.auth(session).read("todo")
                            )
                        ]
                    ).style(padding="20px", height="200px", overflow_y="scroll"),
                    div(
                        textInput().id("todo_item").attr(onkeyup=addOnKeyPress(event)),
                        button("Create").attr(onclick=addTodoIfNotEmpty("todo_item")),
                    ).row(),
                ),
            ).style(
                shadow="0 0 10px rgba(0, 0, 0, 0.5)",
                background_color="white",
                margin="20px",
                padding="20px",
                border_radius="5px",
            ),
        ),
    )
    return web

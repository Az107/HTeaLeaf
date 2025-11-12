from TeaLeaf.Server.ASGI import ASGI
from TeaLeaf.Server.Server import Session
from TeaLeaf.Magic.Store import AuthStore, SuperStore, Store
from TeaLeaf.Magic.LocalState import use_state
from TeaLeaf.Server.Server import HttpRequest
from TeaLeaf.Html.Elements import (
    header,
    checkbox,
    head,
    form,
    html,
    div,
    textInput,
    button,
    h1,
    h2,
    h3,
    submit,
    body,
    script,
    link
)
from TeaLeaf.Magic.MagicComponent import FetchComponent, rButton
from TeaLeaf.utils import enable_reactivity, redirect
from TeaLeaf.Magic.Common import JSCode, Not, Dom
app = ASGI()


def auth_session(session: Session):
    if session.has("userName"):
        return session["userName"]
    return None

enable_reactivity(app)
SuperStore(app)
cstore = Store({"counter": 1})
todoStore = AuthStore(auth_session, {"todo": []})

mincss_url = "https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css"
mincss = link().attr(rel="stylesheet",href=mincss_url)

@app.route("/health")
def health(req: HttpRequest):
    return {
        "status": "ok",
        "method": req.method,
        "path": req.path,
        "body": str(req.json()),
    }



@app.route("/contar")
def contar():

    return div(
        button("-").attr(onclick=cstore.do.update("counter",cstore.read("counter") - 1)),
            h3( cstore.react("counter")),
        button("+").attr(onclick=cstore.do.update("counter", cstore.read("counter") + 1)),
        ).row()



@app.route("/hello/{name}")
def saluda(name):
    return (
        "200 Ok",
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


@app.route("/login")
def user(session, req: HttpRequest):
    if session.has("userName"):
        return "Hello " + session.userName
    user = req.form()
    if user is None or not "userName" in user:
        return "401 unauthorized", LoginPage()
    else:
        session.userName = user["userName"]
        return redirect("/")


@app.route("/example")
def userNav(req: HttpRequest):
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


def elementoCompra(id, task):
    return div(
        checkbox(checked=task["done"]).attr(
            onchange=todoStore.do.update(
                f"todo/{id}/done", not task["done"]
            )
        ),
        h2(task["value"]).style(text_overflow= "ellipsis"),
        button("x").classes("secondary").attr(onclick=todoStore.do.delete(f"todo/{id}"))
    ).row().classes("card")



@app.route("/logout")
def logout(session):
    if session.has("userName"):
        del session["userName"]
    return redirect("/login")

@app.route("/")
def home(session, req: HttpRequest):
    if not session.has("userName"):
        # return redirect("/login")
        session["userName"] = "Alb"

    modal_state = use_state(True)
    age = use_state(0)
    document = JSCode("document")
    window = JSCode("window")
    addTodoIfNotEmpty = JSCode("addTodoIfNotEmpty")
    web = html(
        head(
            mincss,
            script("""
            function addTodoIfNotEmpty(inputId, store) {
                let val = document.getElementById(inputId).value;
                if (val.trim() !== "") {
                    store.set("todo", {"done": false, "value": val});
                    document.getElementById(inputId).value = "";
                } else {
                    alert("empty task")
                }
            }
            """)
        ),
        body(
            header(
                div(
                    h1("TeaLeaf!").style(color="green"),
                    button(f"Welcome {session["userName"]}").attr(onclick=window.location.replace("/logout")),
                ).row()
            ),
            button("toggle modal").attr(onclick=modal_state.set(Not(modal_state.get()))),
            div("Esto es modal").classes("card").row().attr(hidden=modal_state.get()),
            div(
                contar(),
                div([elementoCompra(idx, c) for idx,c in enumerate(todoStore.auth(session).read("todo"))]).style(
                    padding="20px",
                    height="200px",
                    overflow_y="scroll"
                ),
                div(
                    textInput().id("item_compra"),
                    button("Create").attr(
                        onclick=addTodoIfNotEmpty("item_compra",todoStore.do())
                    ),
                ).row(),
            )
        ),
    )
    return web




async def application(scope, receive, send):
    await app.application(scope, receive, send)

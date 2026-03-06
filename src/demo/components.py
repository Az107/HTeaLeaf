from TeaLeaf.Html.Elements import (
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
from TeaLeaf.Magic.Common import JSCode, Not
from TeaLeaf.Magic.HelperMidleware import enable_reactivity
from TeaLeaf.Magic.LocalState import use_state
from TeaLeaf.Magic.Store import AuthStore, Store, SuperStore
from TeaLeaf.Server.Server import HttpRequest, Server, Session
from TeaLeaf.utils import redirect


def auth_session(session: Session):
    if session.has("userName"):
        return session["userName"]
    return None


cstore: Store | None = None
todoStore: AuthStore | None = None

def init(app: Server):
    global cstore
    global todoStore
    print("test")

    enable_reactivity(app)
    SuperStore(app)
    cstore = Store({"counter": 1})
    todoStore = AuthStore(auth_session, {"todo": []})
    app.add_path("/health", health)
    app.add_path("/contar", contar)
    app.add_path("/hello/{name}", saluda)
    app.add_path("/login", user)
    app.add_path("/example", userNav)
    app.add_path("/logout", logout)
    app.add_path("/", home)



mincss_url = "https://cdn.rawgit.com/Chalarangelo/mini.css/v3.0.1/dist/mini-default.min.css"
mincss = link().attr(rel="stylesheet",href=mincss_url)

def health(req: HttpRequest):
    return {
        "status": "ok",
        "method": req.method,
        "path": req.path,
        "body": str(req.json()),
    }



def contar():
    if cstore is None:
        return None

    return div(
        button("-").attr(onclick=cstore.do.update("counter",cstore.read("counter") - 1)),
            h3( cstore.react("counter")),
        button("+").attr(onclick=cstore.do.update("counter", cstore.read("counter") + 1)),
        ).row()



def saluda(name):
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



def user(session, req: HttpRequest):
    if session.has("userName"):
        return "Hello " + session.userName
    user = req.form()
    if user is None or "userName" not in user:
        return 401, LoginPage()
    else:
        session.userName = user["userName"]
        return redirect("/")


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
    if todoStore is None:
        return None

    return div(
        checkbox(checked=task["done"]).attr(
            onchange=todoStore.do.update(
                f"todo/{id}/done", not task["done"]
            )
        ),
        h2(task["value"]).style(text_overflow= "ellipsis"),
        button("x").classes("secondary").attr(onclick=todoStore.do.delete(f"todo/{id}"))
    ).row().classes("card")




def logout(session):
    if session.has("userName"):
        del session["userName"]
    return redirect("/login")


def home(session, req: HttpRequest):
    if todoStore is None:
        return None

    if not session.has("userName"):
        return redirect("/login")


    modal_state = use_state(True)
    age = use_state(0)
    _document = JSCode("document")
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
            """),
            age.new(),
            modal_state.new()
        ),
        body(
            header(
                div(
                    h1("TeaLeaf!").style(color="green"),
                    button(f"Welcome {session["userName"]}").attr(onclick=window.location.replace("/logout")),
                ).row()
            ),
            button("toggle modal").attr(onclick=modal_state.set(Not(modal_state.get()))),
            div("Esto es modal: ", modal_state()).classes("card").row().attr(hidden=modal_state.get()),
            div(
                button("-").attr(onclick=age.set(age.get() - 1)),
                age(),
                button("+").attr(onclick=age.set(age.get() + 1))
            ).classes("card").row(),
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
                        onclick=addTodoIfNotEmpty("item_compra",todoStore)
                    ),
                ).row(),
            )
        ),
    )
    return web

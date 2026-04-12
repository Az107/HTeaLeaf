# 🍃 HTeaLeaf

**HTeaLeaf** is a *declarative web framework for Python* —
build dynamic, reactive web apps using **pure Python**, without writing templates or frontend JavaScript manually.

> ⚠️ Currently in alpha — stable enough for experimentation and demos, but the public API may still change before beta.

---

## ✨ Overview

HTeaLeaf merges ideas from modern frontend frameworks (React, Svelte, SolidJS)
with the simplicity of Python web servers.

You declare HTML directly in Python, manage reactive state via `Store` objects,
and HTeaLeaf takes care of keeping everything in sync automatically.

---

## 🚀 Quick Example

```python
from HTeaLeaf.Server.WSGI import WSGI
from HTeaLeaf.Magic.Store import Store, SuperStore
from HTeaLeaf.Html.Elements import div, h3, button

app = WSGI()
SuperStore(app)

counter = Store({"count": 0})

@app.route("/")
def home():
    return div(
        button("-").attr(onclick=counter.js.update("count", -1)),
        h3(counter.react("count")),
        button("+").attr(onclick=counter.js.update("count", 1)),
    )

application = app.wsgi_app

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server("", 8000, application) as server:
        print("Serving at http://127.0.0.1:8000")
        server.serve_forever()
```

Visit `http://127.0.0.1:8000` — a fully reactive counter, zero JavaScript written by hand.

You can also write client-side logic directly in Python using the `@js` decorator,
and HTeaLeaf will compile it to JavaScript automatically:

```python
from HTeaLeaf.Magic.JSCode import js

@js
def greet(event):
    console.log("hello from Python-compiled JS!")

button("Click me").attr(onclick=greet)
```

---

## ✨ Key Features

- **Declarative HTML** — build DOM trees with a fluent Python DSL, no templates needed
- **Reactive server state** — `Store` objects stay in sync with the UI automatically
- **Local route state** — `use_state()` for state scoped to a single route
- **Python → JS transpilation** — write client-side logic in Python with `@js`; HTeaLeaf compiles it
- **Session support** — per-user state with `AuthStore` and cookies

---

## 📦 Installation

```bash
pip install htealeaf
```

---

## 🗺️ Roadmap

- [x] Declarative HTML DSL
- [x] Path-based routing
- [x] Server-side reactive state (`Store`, `AuthStore`)
- [x] Python → JavaScript transpiler
- [x] Local route state (`use_state()`)
- [x] Session support
- [x] Client-side-only state (no server round-trip)
- [ ] Persistent Store backends (Redis, SQL, …)
- [ ] CLI
- [ ] Render optimisation

---

## 📖 Documentation

Full documentation is available in the [Wiki](https://github.com/Az107/HTeaLeaf/wiki/Welcome-to-the-HTeaLeaf!).

---

## 🤝 Ecosystem

HTeaLeaf is part of a tea-themed open-source ecosystem by [@Az107](https://github.com/Az107):

| Project | Language | Description |
|---|---|---|
| **HTeaPot** | Rust | HTTP server — plays on HTTP 418 "I'm a teapot" |
| **HTeaLeaf** | Python | This framework — SSR with reactive state and JS transpilation |
| **Cafetera** | Rust | API mocker for testing, built on top of HTeaPot |

---

## License

MIT License © 2026 — HTeaLeaf Framework. Made with 🍃 and Python.

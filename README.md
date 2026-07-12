# 🍃 HTeaLeaf

**HTeaLeaf** is a *declarative web framework for Python* —
build dynamic, reactive web apps using **pure Python**, without writing templates or frontend JavaScript manually.

>⚠️ Beta — HTeaLeaf is usable and the core API is stable, but you may encounter performance issues or unexpected bugs. Not recommended for production yet. Feedback and bug reports are very welcome.

---

## ✨ Overview

HTeaLeaf merges ideas from modern frontend frameworks (React, Svelte, SolidJS)
with the simplicity of Python web servers.

You declare HTML directly in Python, manage reactive state via `Store` objects,
and HTeaLeaf takes care of keeping everything in sync automatically.

---

## 📦 Installation

```bash
pip install htealeaf
```

Requires **Python ≥ 3.10**. Bring your own WSGI/ASGI server (`wsgiref` from the
standard library works for local development, `uvicorn` for ASGI).

---

## 🚀 Quick Example

```python
from htealeaf import HteaLeaf, SuperStore, Store, adapters
from htealeaf.elements import div, h3, button

app = HteaLeaf(adapters.WSGI)
SuperStore(app)  # wires the store API routes and client-side runtime

counter = Store({"count": 0})

@app.route("/")
def home():
    return div(
        button("-").attr(onclick=counter.js.update("count", counter.read("count") - 1)),
        h3(counter.read("count")),
        button("+").attr(onclick=counter.js.update("count", counter.read("count") + 1)),
    )

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server("", 8000, app) as server:
        print("Serving at http://127.0.0.1:8000")
        server.serve_forever()
```

Visit `http://127.0.0.1:8000` — a fully reactive counter, zero JavaScript written by hand.

You can also write client-side logic directly in Python using the `@js` decorator,
and HTeaLeaf will compile it to JavaScript automatically:

```python
from htealeaf.js import js
from htealeaf.js.common import console

@js
def greet(event):
    console.log("hello from Python-compiled JS!")

button("Click me").attr(onclick=greet)
```

> **Note:** the `HteaLeaf` app object is itself the WSGI/ASGI callable — pass it
> straight to your server (`make_server("", 8000, app)`), there is no separate
> `.wsgi_app` attribute.

---

## ⚡ ASGI

The same app runs under ASGI by swapping the adapter:

```python
from htealeaf import HteaLeaf, SuperStore, adapters

app = HteaLeaf(adapters.ASGI)
SuperStore(app)
# ... routes ...
```

```bash
uvicorn myapp:app
```

A `CGI` adapter is also available (`adapters.CGI`).

---

## ✨ Key Features

- **Declarative HTML**: build DOM trees with a fluent Python DSL, no templates needed
- **Reactive server state**: `Store` objects stay in sync with the UI automatically
- **Local route state**: `use_state()` for state scoped to a single route (client-side, no server round-trip)
- **Python → JS transpilation**: write client-side logic in Python with `@js`; HTeaLeaf compiles it
- **Session support**: per-user state with `AuthStore` and cookies
- **Multiple transports**: WSGI, ASGI, and CGI adapters behind one API

---

## 🧩 Running the demo

The repository ships a small demo app:

```bash
python -m demo.demo_wsgi     # WSGI on http://127.0.0.1:8000
uvicorn demo.demo_asgi:app   # ASGI
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
- [x] Async first architecture
- [ ] Render optimisation
- [ ] Persistent Store backends (Redis, SQL, …)
- [ ] Session expiration (TTL + eviction) — in progress on `feature/alb-28`
- [ ] CLI
- [ ] Build system to static assets

---

## 📖 Documentation

- Full documentation: [Wiki](https://github.com/Az107/HTeaLeaf/wiki/Welcome-to-the-HTeaLeaf!)
- [`docs/PY2JS.md`](docs/PY2JS.md) — design notes for the Python → JavaScript (`JSCode`) interop layer

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

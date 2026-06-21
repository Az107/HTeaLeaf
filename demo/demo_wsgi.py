from HTeaLeaf import HteaLeaf, adapters

from .components import init

app = HteaLeaf(adapters.WSGI)

init(app)

if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    with make_server("", 8000, app) as server:
        print("Serving on http://127.0.0.1:8000")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\rBye")

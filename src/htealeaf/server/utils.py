
def redirect(path: str):
    return 302, [("Location", path)], ""

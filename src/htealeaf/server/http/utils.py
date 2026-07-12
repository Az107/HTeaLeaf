from email.message import Message


def get_boundary(content_type: str) -> bytes:
    msg = Message()
    msg["content-type"] = content_type
    boundary = msg.get_param("boundary")
    if boundary is None:
        raise ValueError("No boundary in content-type header")
    boundary = str(boundary)
    return boundary.encode("latin-1") if isinstance(boundary, str) else boundary


def parse_content_disposition(disposition: str) -> tuple[str | None, str | None]:
    msg = Message()
    msg["content-disposition"] = disposition
    name = msg.get_param("name", header="content-disposition")
    filename = msg.get_param("filename", header="content-disposition")
    name = str(name) if name is not None else ""
    filename = str(filename) if filename is not None else ""
    return name, filename

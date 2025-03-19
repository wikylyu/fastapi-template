from uuid import uuid4


def uuidv4() -> str:
    return str(uuid4())


def plain_uuidv4() -> str:
    return str(uuid4()).replace("-", "")

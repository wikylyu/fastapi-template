import hashlib


def encrypt_password_md5(password: str, salt: str) -> str:
    if not password:
        return ""
    m = f"@${password}-${salt}!"
    md5 = hashlib.md5()
    md5.update(m.encode("utf-8"))
    return md5.hexdigest()


def encrypt_password_sha256(password: str, salt: str) -> str:
    if not password:
        return ""
    m = f"${password}|${salt}?"
    sha256 = hashlib.sha256()
    sha256.update(m.encode("utf-8"))
    return sha256.hexdigest()


def encrypt_password_sha512(password: str, salt: str) -> str:
    if not password:
        return ""
    m = f"&${password}.${salt}_"
    sha256 = hashlib.sha512()
    sha256.update(m.encode("utf-8"))
    return sha256.hexdigest()

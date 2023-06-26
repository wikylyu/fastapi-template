import random
import string


def random_string(len: int) -> str:
    return ''.join(random.choice(string.ascii_letters) for i in range(len))


def random_digit(len: int) -> str:
    return ''.join(random.choice(string.digits) for i in range(len))

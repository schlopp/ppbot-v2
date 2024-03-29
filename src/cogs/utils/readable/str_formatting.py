import random

__all__ = ("scramble", "uncopyable")


def _shuffle(string):
    """
    Shuffles a string.
    """

    string = list(string)
    random.shuffle(string)
    return "".join(string)


def scramble(string):
    """
    Scrambles a string.
    """

    return " ".join([_shuffle(word) for word in string.split()])


def uncopyable(string):
    """
    Makes a string uncopyable.
    """

    return "\u200D".join(string)

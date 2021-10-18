import random

__all__ = ("scramble",)


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

import typing

__all__ = ("int_to_roman",)


def int_to_roman(n: int, *, emoji_mode: typing.Optional[bool] = False) -> str:
    """
    Given an integer, convert it to a roman numeral.

    Args:
        n (int): The integer to convert. Must be within the range of `0` to `3999`.
        emoji_mode (bool, optional): If `True`, the output will be a string of emojis.
    """
    if not isinstance(n, int):
        raise TypeError("can only")

    if not n:
        return "<:ROMAN_NOTHING:881601079618453505>" if emoji_mode else "0"

    if not emoji_mode:
        M = [
            "",
            "M",
            "MM",
            "MMM",
        ]
        C = [
            "",
            "C",
            "CC",
            "CCC",
            "CD",
            "D",
            "DC",
            "DCC",
            "DCCC",
            "CM",
        ]
        X = [
            "",
            "X",
            "XX",
            "XXX",
            "XL",
            "L",
            "LX",
            "LXX",
            "LXXX",
            "XC",
        ]
        I = [
            "",
            "I",
            "II",
            "III",
            "IV",
            "V",
            "VI",
            "VII",
            "VIII",
            "IX",
        ]

    else:
        emojis = {
            "M": "<:ROMAN_M:881593701850316831>",
            "C": "<:ROMAN_C:881594369549938688>",
            "D": "<:ROMAN_D:881594987580637184>",
            "X": "<:ROMAN_X:881597391034269707>",
            "L": "<:ROMAN_L:881597774808907787>",
            "I": "<:ROMAN_I:881598680015188038>",
            "V": "<:ROMAN_V:881599773919047730>",
        }
        M = [
            "",
            emojis["M"],
            emojis["M"] * 2,
            emojis["M"] * 3,
        ]
        C = [
            "",
            emojis["C"],
            emojis["C"] * 2,
            emojis["C"] * 3,
            emojis["C"] + emojis["D"],
            emojis["D"],
            emojis["D"] + emojis["C"],
            emojis["D"] + emojis["C"] * 2,
            emojis["D"] + emojis["C"] * 3,
            emojis["D"] + emojis["M"],
        ]
        X = [
            "",
            emojis["X"],
            emojis["X"] * 2,
            emojis["X"] * 3,
            emojis["X"] + emojis["L"],
            emojis["L"],
            emojis["L"] + emojis["X"],
            emojis["L"] + emojis["X"] * 2,
            emojis["L"] + emojis["X"] * 3,
            emojis["L"] + emojis["C"],
        ]
        I = [
            "",
            emojis["I"],
            emojis["I"] * 2,
            emojis["I"] * 3,
            emojis["I"] + emojis["V"],
            emojis["V"],
            emojis["V"] + emojis["I"],
            emojis["V"] + emojis["I"] * 2,
            emojis["V"] + emojis["I"] * 3,
            emojis["I"] + emojis["X"],
        ]

    try:
        return M[n // 1000] + C[(n % 1000) // 100] + X[(n % 100) // 10] + I[n % 10]
    except IndexError:
        raise ValueError(
            f'Expected "int" within the range of `0` to `3999`, got `{n}` instead.'
        )

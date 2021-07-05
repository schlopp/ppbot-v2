import random


def int_to_roman(n: int) -> str:
    """
    Convert an int to a roman numeral. Works well enough.
    """

    val = [
        1000, 900, 500,
        400, 100, 90,
        50, 40, 10,
        9, 5, 4,
        1,
    ]
    syb = [
        "M", "CM", "D",
        "CD", "C", "XC",
        "L", "XL", "X",
        "IX", "V", "IV",
        "I",
    ]
    roman_n = ""
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_n += syb[i]
            n -= val[i]
        i += 1
    return roman_n

def random_name() -> str:
    return random.choice([
        'Obama',
        'Dick roberts',
        'Johnny from Johhny Johhny yes papa',
        'Shrek',
        'Caleb',
        'Bob',
        'Walter',
        'Napoleon bonaparte',
        'Bob ross',
        'Thanos',
        'Don vito',
        'Bill cosby',
        'Your step-sis',
        'Pp god',
        'Random guy',
        'Genie',
        'Your mom',
        'Your daughter',
        'Big Man Tyrone',
        'Vin Diesel',
        'Ben Shapiro',
        'Local bitchboy',
        'Average pp bot enjoyer',
    ])

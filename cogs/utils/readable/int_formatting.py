"""
Functions that take an int as input and return a string.
"""

def int_to_roman(n: int):
    """
    Given an integer, convert it to a roman numeral.

    Args:
        n (int): The integer to convert. Must be within the range of `0` to `3999`.
    """
    if not isinstance(n, int):
        raise TypeError("can only")
    
    if not n:
        return '0'

    M = ["", "M", "MM", "MMM"]
    C = ["", "C", "CC", "CCC", "CD", "D", "DC", "DCC", "DCCC", "CM"]
    X = ["", "X", "XX", "XXX", "XL", "L", "LX", "LXX", "LXXX", "XC"]
    I = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]

    try:
        return M[n // 1000] + C[(n % 1000) // 100] + X[(n % 100) // 10] + I[n % 10]
    except IndexError:
        raise ValueError(f"Expected \"int\" within the range of `0` to `3999`, got `{n}` instead.")

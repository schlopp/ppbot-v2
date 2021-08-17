import voxelbotutils as vbu


def get_level_by_exp(exp) -> int:
    """
    Returns the level of the player based on the amount of exp.
    """

    exp_per_level = [
        0,       50,     175,        # 1  2  3
        375,     675,    1_175,      # 4  5  6
        1_925,   2_925,  4_425,      # 7  8  9
        6_425,   9_925,  14_925,     # 10 11 12
        22_425,  32_425, 47_425,     # 13 14 15
        67_425,  97_425, 147_425,    # 16 17 18
        222_425, 322_425             # 19 20
    ]
    for n, i in enumerate(exp_per_level):
        if exp <= i:
            return n + 1

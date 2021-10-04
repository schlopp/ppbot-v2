"""
Functions that format rewards.
"""

import random
import re
import typing

from .. import LootableItem


__all__ = ("format_rewards",)


def format_rewards(
    *,
    inches: typing.Optional[int] = None,
    items: typing.Optional[typing.List[LootableItem]] = None,
):
    """
    fuckin text
    """

    # there should be a comment here
    items_as_text = []

    if not inches:

        # No reward
        if not items:
            return "**{}**".format(
                random.choice(
                    [
                        "literally nothing",
                        "nothing lmao",
                        "nothing L",
                        "nothing <a:KEK_COMFY:884797245621420102>",
                    ]
                )
            )

        # Just items as reward
        item: LootableItem
        for item in items:

            # Some grammar stuff to make this flow better
            if item.amount == 1:
                article = (
                    "an" if re.match(r"^[aeiou]", item.name, re.IGNORECASE) else "a"
                )
                items_as_text.append(f"{article} **{item.emoji} {item.name}**")

            else:
                plural = "" if re.match(r".*s$", item.name, re.IGNORECASE) else "s"
                items_as_text.append(
                    f"{item.amount}x **{item.emoji} {item.name}**{plural}"
                )

        if len(items_as_text) == 1:
            return items_as_text[0]
        return "{} and {}".format(", ".join(items_as_text[:-1]), items_as_text[-1])

    else:

        if not items:
            return "**+{} {}**".format(
                inches,
                random.choice(
                    [
                        "cock size",
                        "pp size",
                        "peepee size",
                        "dick size",
                        "inches",
                    ]
                ),
            )

    item: LootableItem
    for item in items:
        # Some grammar stuff to make this flow better
        if item.amount == 1:
            article = "an" if re.match(r"^[aeiou]", item.name, re.IGNORECASE) else "a"
            items_as_text.append(f"{article} **{item.emoji} {item.name}**")
        else:
            plural = "" if re.match(r".*s$", item.name, re.IGNORECASE) else "s"
            items_as_text.append(f"{item.amount}x **{item.emoji} {item.name}**{plural}")

    return "{} and {}".format(
        ", ".join(items_as_text),
        "**+{} {}**".format(
            inches,
            random.choice(
                [
                    "cock size",
                    "pp size",
                    "peepee size",
                    "dick size",
                    "inches",
                ]
            ),
        ),
    )

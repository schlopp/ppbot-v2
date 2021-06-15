import typing
import voxelbotutils as vbu
from cogs.utils import Item, Dict, Lore, ShopSettings


class ItemNotFoundError(Exception):
    """
    Raised when a item is not found in the database.
    """

async def fetch_item(item_name:str):
    """
    Fetch an item from the database.
    This function is a coroutine.
    ## Args:
    name|type|description
    -|-|-
    item_name|`str`|The item name.
    raises :class:`ItemNotFoundError` when the item is not found in the database.
    """

    async with vbu.DatabaseConnection() as db:
        fetched = await db('''SELECT * FROM items WHERE name=$1''', item_name)
        if not fetched:
            raise ItemNotFoundError(f"Item '{item_name}' not found in the database.")

        item_dict = fetched[0]
        return Item(
            item_dict['name'],
            requires=Dict.from_json(item_dict['requires']),
            type=item_dict['type'],
            shopsettings=ShopSettings.from_json(item_dict['shopsettings']),
            rarity=item_dict['rarity'],
            auctionable=item_dict['auctionable'],
            emoji=item_dict['emoji'],
            recipe=Dict.from_json(item_dict['recipe']),
            used_for=item_dict['used_for'],
            recipes=Dict.from_json(item_dict['recipes']),
            buffs=[Dict.from_json(i) for i in item_dict['buffs']],
            lore=Lore(
                item_dict['description'],
                item_dict['story'],
            ),
        )
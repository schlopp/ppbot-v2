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
    ---
    raises :class:`ItemNotFoundError` when the item is not found in the database.
    """

    async with vbu.DatabaseConnection() as db:
        rows = await db('''SELECT * FROM items WHERE name=$1''', item_name)
        if not rows:
            raise ItemNotFoundError(f"Item '{item_name}' not found in the database.")

        row = rows[0]
        return Item(
            row['name'],
            requires=Dict.from_json(row['requires']),
            type=row['type'],
            shopsettings=ShopSettings(row['shop_for_sale'], row['shop_buy'], row['shop_sell']),
            rarity=row['rarity'],
            auctionable=row['auctionable'],
            emoji=row['emoji'],
            recipe=Dict.from_json(row['recipe']),
            used_for=row['used_for'],
            recipes=Dict.from_json(row['recipes']),
            buffs=[Dict.from_json(i) for i in row['buffs']],
            lore=Lore(
                row['description'],
                row['story'],
            ),
        )

async def fetch_items(db:vbu.DatabaseConnection, for_sale:typing.Optional[bool]=None, auctionable:typing.Optional[bool]=None):
    """
    Fetch multiple items from the database.
    This function is a coroutine.
    ## Args:
    name|type|description
    -|-|-
    for_sale|`typing.Optional[bool] = None`|Only select items that are for sale.
    auctionable|`typing.Optional[bool] = None`|Only select items that are auctionable.
    ---
    """

    if for_sale is None and auctionable is None:
        rows = await db('''SELECT * FROM items''')
    
    elif for_sale is not None and auctionable is not None:
        if auctionable is not None:
            rows = await db('''SELECT * FROM items WHERE shop_for_sale = $1 AND auctionable = $2''', for_sale, auctionable)
        else:
            rows = await db('''SELECT * FROM items WHERE auctionable = $1''', auctionable)
    
    else:
        rows = await db('''SELECT * FROM items WHERE shop_for_sale = $1''', for_sale)


    return [
        Item(
            row['name'],
            requires=Dict.from_json(row['requires']),
            type=row['type'],
            shopsettings=ShopSettings(row['shop_for_sale'], row['shop_buy'], row['shop_sell']),
            rarity=row['rarity'],
            auctionable=row['auctionable'],
            emoji=row['emoji'],
            recipe=Dict.from_json(row['recipe']),
            used_for=row['used_for'],
            recipes=Dict.from_json(row['recipes']),
            buffs=[Dict.from_json(i) for i in row['buffs']],
            lore=Lore(
                row['description'],
                row['story'],
            ),
        ) for row in rows
    ]
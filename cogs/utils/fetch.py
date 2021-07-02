import typing
import voxelbotutils as vbu
from cogs.utils import Item, Dict, Lore, ShopSettings


class ItemNotFoundError(Exception):
    """
    Raised when a item is not found in the database.
    """

async def fetch_item(item_name: str, db: vbu.DatabaseConnection) -> Item:
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

    rows = await db("""SELECT * FROM items WHERE name=$1""", item_name)
    if not rows:
        raise ItemNotFoundError(f"Item '{item_name}' not found in the database.")

    row = rows[0]
    return Item.from_record(row)

async def fetch_items(
        db: vbu.DatabaseConnection,
        for_sale: typing.Optional[bool] = None,
        auctionable: typing.Optional[bool] = None,
    ) -> typing.List[Item]:
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
        rows = await db("""SELECT * FROM items""")

    elif for_sale is not None and auctionable is not None:
        if auctionable is not None:
            rows = await db(
                """SELECT * FROM items WHERE shop_for_sale = $1 AND auctionable = $2""",
                for_sale,
                auctionable,
            )
        else:
            rows = await db(
                """SELECT * FROM items WHERE auctionable = $1""", auctionable
            )

    else:
        rows = await db("""SELECT * FROM items WHERE shop_for_sale = $1""", for_sale)

    return [Item.from_record(row) for row in rows]

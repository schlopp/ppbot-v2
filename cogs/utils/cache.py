import asyncio
import voxelbotutils as vbu
from cogs.utils import fetch_items

async def fetch():
    async with vbu.DatabaseConnection() as db:
        for_sale = await fetch_items(db, for_sale=True)
        auctionable = await fetch_items(db, auctionable=True)
        not_for_sale = await fetch_items(db, for_sale=False)
        not_auctionable = await fetch_items(db, auctionable=False)
        items = await fetch_items(db)
    
    return (
        for_sale,
        auctionable,
        not_for_sale,
        not_auctionable,
        items,
    )

for_sale, auctionable, not_for_sale, not_auctionable, items = asyncio.run(fetch())

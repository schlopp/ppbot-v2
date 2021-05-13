import asyncpg
import toml
from discord.ext import commands

with open("./config.toml") as f:
    config = toml.loads(f.read())


class Shop(dict):
    def __init__(self):
        pass
    
    @classmethod
    async def fetch(cls, multiplier):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.shopItems''')
        await conn.close()
        self = cls()
        for i in fetched:
            i = dict(i)
            self[i["item_name"]] = {
                "type": i["item_type"],
                "description": i["item_desc"],
                "default_price": i["default_price"],
                "multiplier_dependent": i["multiplier_dependent"],
                "sell_for": i["sell_for"],
                "gain": i["gain"],
                "price": int(i["default_price"] * i["default_multiplier"] ** 1.3) if i["multiplier_dependent"] else i["default_price"]
            }
        return self
    
    @staticmethod
    async def add_item(item_name:str, item_type:str, item_desc:str, default_price:int, multiplierDependant:bool = False):
        await conn.execute(
            '''
            INSERT INTO userdata.shopItems(item_name, item_type, item_desc, default_price, multiplierDependent) VALUES($1, $2, $3, $4, $5)
            ON CONFLICT (item_name) DO NOTHING;
            ''',
            item_name,
            item_type,
            item_desc,
            default_price,
            multiplierDependant
        )
        await conn.close()

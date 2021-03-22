import asyncpg
import toml

with open("./config.toml") as f:
    config = toml.loads(f.read())


class Inv:
    def __init__(self, user_id:int):
        self.user_id = user_id
    
    
    async def fetch_all(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.inv WHERE user_id = $1''',self.user_id)
        await conn.close()
        items = {}
        for i in fetched:
            items[dict(i)["item_name"]] = dict(i)["amount"]
        return items if items else {}
    
    
    async def has_item(self, item_name:str) -> bool:
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.inv WHERE user_id = $1 AND item_name = $2''',self.user_id,item_name)
        await conn.close()
        return True if fetched and dict(fetched[0])["amount"]>0 else False
    
    
    async def new_item(self, item_name:str, amount:int=1):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            INSERT INTO userdata.inv (user_id, item_name, amount) VALUES ($1, $2, $3)
            ON CONFLICT (user_id, item_name) DO
            UPDATE SET amount = userdata.inv.amount + $3;
        ''',
        self.user_id,           #$1 user_id
        item_name,              #$2 item_name
        amount)                 #$3 amount
        return await conn.close()
    
    
    async def fetch_item(self, item_name:str):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.inv WHERE user_id = $1 AND item_name = $2''',self.user_id,item_name)
        await conn.close()
        return dict(fetched[0]) if fetched else {"user_id":self.user_id,"item_name":item_name,"amount":0}

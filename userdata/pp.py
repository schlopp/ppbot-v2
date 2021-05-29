import asyncpg
import toml
import aiohttp
from discord.ext import commands


with open("./config.toml") as f:
    config = toml.loads(f.read())

class Pp:

    def __init__(self, user_id=None):
        self.user_id = user_id
    
    def __bool__(self):
        if hasattr(self, 'size'):
            return True
        return False
    
    @classmethod
    async def fetch(cls, user_id:int, bot:commands.AutoShardedBot=None, get_multiplier:bool=True):
        """
        Gets the current PP object data for a given user.
        """

        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.pp WHERE user_id=$1''', user_id)
        await conn.close()

        if not fetched:
            return cls()
        
        self = cls(user_id)
        self.name = fetched[0]["pp_name"]
        self.size = fetched[0]["pp_size"]
        self.default_multiplier = fetched[0]["multiplier"]
        
        if get_multiplier and bot:
            url = f"https://top.gg/api/bots/{bot.user.id}/check"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params={"userId": user_id}, headers={"Authorization": config["dbl"]["TOKEN"]}) as r:
                    self.multiplier = {
                        "multiplier": fetched[0]["multiplier"],
                        "voted":False,
                        }
                    try:
                        data = await r.json()                        
                        if r.status == 200 and data.get("voted", False):
                            self.multiplier = {
                        "multiplier": fetched[0]["multiplier"] * 2,
                                "voted":True,
                                }
                    except Exception:
                        pass
        return self

    async def create(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''INSERT INTO userdata.pp(user_id, pp_name, pp_size, multiplier) VALUES($1, 'Unnamed Pp', 0, 1)
            ON CONFLICT (user_id) DO NOTHING;''', self.user_id)
        await conn.close()
    
    async def delete(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''DELETE FROM userdata.pp WHERE user_id = $1;''', self.user_id)
        await conn.close()
    
    async def update(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''UPDATE userdata.pp SET pp_name = $1, pp_size = $2, multiplier = $3 WHERE user_id = $4''', self.name, self.size, self.default_multiplier, self.user_id)
        await conn.close()
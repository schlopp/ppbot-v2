import asyncpg
import toml

with open("../config.toml") as f:
    config = toml.loads(f.read())

class Pp:
    def __init__(self, user_id:int):
        self.user_id = user_id
    

    async def pp_name(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT pp_name FROM userdata.pp WHERE user_id = $1''',self.user_id)
        await conn.close()
        return dict(fetched[0])["pp_name"] if fetched else None
    

    async def pp_size(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT pp_size FROM userdata.pp WHERE user_id = $1''',self.user_id)
        await conn.close()
        return dict(fetched[0])["pp_size"] if fetched else None
    

    async def multiplier(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT multiplier FROM userdata.pp WHERE user_id = $1''',self.user_id)
        await conn.close()
        return dict(fetched[0])["multiplier"] if fetched else None
     

    async def check(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.pp WHERE user_id = $1;''',self.user_id)
        await conn.close()
        return True if fetched else False
    

    async def create(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            INSERT INTO userdata.pp(user_id, pp_name, pp_size, multiplier) VALUES($1, $2, $3, $4)
            ON CONFLICT (user_id) DO NOTHING;
        ''',
        self.user_id,
        "Unnamed Pp",
        0,
        1)
        return await conn.close()
    
    
    async def delete(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            DELETE FROM userdata.pp WHERE user_id = $1 RETURNING *;
        ''',
        self.user_id)
        return await conn.close()
    
    
    async def size_add(self, amount:int):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            UPDATE userdata.pp SET pp_size = userdata.pp.pp_size + $2 WHERE userdata.pp.user_id = $1;
        ''',
        self.user_id,
        amount)
        return await conn.close()
    
    
    async def multiplier_add(self, amount:int):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            UPDATE userdata.pp SET multiplier = userdata.pp.multiplier + $2 WHERE userdata.pp.user_id = $1;
        ''',
        self.user_id,
        amount)
        return await conn.close()
    
    
    async def rename(self, pp_name:str):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            UPDATE userdata.pp SET pp_name = $2 WHERE userdata.pp.user_id = $1;
        ''',
        self.user_id,
        pp_name)
        return await conn.close()

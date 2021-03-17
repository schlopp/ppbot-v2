import asyncpg
import toml

with open("./config.toml") as f:
    config = toml.loads(f.read())


class Event:
    def __init__(self, channel_id:int, answer:str):
        self.channel_id = channel_id
        self.answer = answer
        self.getevent = 'SELECT * FROM userdata.events WHERE channel_id = $1 AND answer = $2;'

    
    async def first(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT first_place FROM userdata.events WHERE channel_id = $1 AND answer = $2;''',self.channel_id,self.answer)
        await conn.close()
        return dict(fetched[0])["first_place"] if dict(fetched[0])["first_place"] != 1 else None
    
    
    async def second(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT second_place FROM userdata.events WHERE channel_id = $1 AND answer = $2;''',self.channel_id,self.answer)
        await conn.close()
        return dict(fetched[0])["second_place"] if dict(fetched[0])["second_place"] != 1 else None
    
    
    async def third(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT third_place FROM userdata.events WHERE channel_id = $1 AND answer = $2;''',self.channel_id,self.answer)
        await conn.close()
        return dict(fetched[0])["third_place"] if dict(fetched[0])["third_place"] != 1 else None
    
    
    async def check(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch(self.getevent,self.channel_id,self.answer)
        await conn.close()
        return True if fetched else False
    
    
    async def create(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            INSERT INTO userdata.events (channel_id, answer) VALUES ($1, $2)
            ON CONFLICT (channel_id, answer) DO NOTHING;
        ''',self.channel_id,self.answer)
        return await conn.close()
    
    
    async def delete(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            DELETE FROM userdata.events WHERE channel_id = $1 AND answer = $2;
        ''',self.channel_id,self.answer)
        return await conn.close()
    
    
    async def unplayable(self, user_id:int):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch(self.getevent,self.channel_id,self.answer)
        fetched = dict(fetched[0])
        if fetched["third_place"] != 1:
            return 2
        for i in fetched.values():
            if i == user_id:
                return 1

    
    async def setplace(self, user_id:int):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch(self.getevent,self.channel_id,self.answer)
        fetched = dict(fetched[0])
        for i in fetched.items():
            if list(i)[1] == 1:
                await conn.execute(f'''UPDATE userdata.events SET {list(i)[0]} = $1 WHERE channel_id = $2 AND answer = $3;''',user_id,self.channel_id,self.answer)
                return list(i)[0]

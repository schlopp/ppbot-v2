import asyncpg
import toml
import copy

with open("./config.toml") as f:
    config = toml.loads(f.read())


class Inv(dict):
    def __init__(self, user_id:int):
        self.user_id = user_id
        self.new_items = []
    
    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        self.new_items.append(key)
        self[key] = 0
        return 0
    
    async def __aenter__(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.inv WHERE user_id = $1''',self.user_id)
        await conn.close()
        items = {}
        for i in fetched:
            self[dict(i)["item_name"]] = dict(i)["amount"]
        self.old_inv = copy.deepcopy(self)
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        insertvalues = ''
        updatevalues = []
        
        for key, value in self.items():
            if key in self.new_items:
                insertvalues += f'({self.user_id}, \'{key}\', {value}),'
            elif self[key] != self.old_inv[key]:
                updatevalues.append((key,value))
                
        if insertvalues:
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n\n\n',insertvalues.rstrip(','))
            await conn.execute(
                f'''INSERT INTO userdata.inv(user_id, item_name, amount) VALUES {insertvalues.rstrip(',')}''')
            
        for i in updatevalues:
            await conn.execute('''
                UPDATE userdata.inv
                SET
                    amount = $1
                WHERE
                    item_name = $2 AND user_id = $3;
                ''',
                i[0],
                i[1],
                self.user_id)
        await conn.close()
    
    @classmethod
    async def fetch(cls, user_id):
        self = cls(user_id)
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.inv WHERE user_id = $1''',self.user_id)
        await conn.close()
        items = {}
        for i in fetched:
            self[dict(i)["item_name"]] = dict(i)["amount"]
        self.old_inv = self
        return self
    
    async def update(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        insertvalues = ''
        updatevalues = []
        
        for key, value in self.items():
            if key in self.new_items:
                insertvalues += f'({self.user_id}, \'{key}\', {value}),'
            elif self[key] != self.old_inv[key]:
                updatevalues.append((key,value))
                
        if insertvalues:
            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n\n\n',insertvalues.rstrip(','))
            await conn.execute(
                f'''INSERT INTO userdata.inv(user_id, item_name, amount) VALUES {insertvalues.rstrip(',')}''')
            
        for i in updatevalues:
            await conn.execute('''
                UPDATE userdata.inv
                SET
                    amount = $1
                WHERE
                    item_name = $2 AND user_id = $3;
                ''',
                i[0],
                i[1],
                self.user_id)
        await conn.close()
    
    async def has_item(self, item_name:str) -> bool:
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT * FROM userdata.inv WHERE user_id = $1 AND item_name = $2''',self.user_id,item_name)
        await conn.close()
        return True if fetched and dict(fetched[0])["amount"]>0 else False

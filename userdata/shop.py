import asyncpg
import toml

with open("./config.toml") as f:
    config = toml.loads(f.read())


class Shop:
    def __init__(self):
        """Init isn't needed lmao this is more like a group don't judge""" 
        pass
    
    
    async def items(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        fetched = await conn.fetch('''SELECT item_name FROM userdata.shopItems''')
        await conn.close()
        return [Shop.Item(dict(i)["item_name"]) for i in fetched]
    
    
    class Item:
        def __init__(self, item_name:str):
            self.item_name = item_name
        
        async def item_type(self):
            conn = await asyncpg.connect(config['admin']['PSQL'])
            fetched = await conn.fetch('''SELECT item_type FROM userdata.shopItems WHERE item_name = $1''',self.item_name)
            await conn.close()
            return dict(fetched[0])["item_type"] if fetched else None
          
         
        async def item_desc(self):
            conn = await asyncpg.connect(config['admin']['PSQL'])
            fetched = await conn.fetch('''SELECT item_desc FROM userdata.shopItems WHERE item_name = $1''',self.item_name)
            await conn.close()
            return dict(fetched[0])["item_desc"] if fetched else None
          
          
        async def default_price(self):
            conn = await asyncpg.connect(config['admin']['PSQL'])
            fetched = await conn.fetch('''SELECT default_price FROM userdata.shopItems WHERE item_name = $1''',self.item_name)
            await conn.close()
            return dict(fetched[0])["default_price"] if fetched else None
          
          
        async def multiplierdependent(self):
            conn = await asyncpg.connect(config['admin']['PSQL'])
            fetched = await conn.fetch('''SELECT multiplierdependent FROM userdata.shopItems WHERE item_name = $1''',self.item_name)
            await conn.close()
            return dict(fetched[0])["multiplierdependent"] if fetched else False
        
        
        async def sell_for(self):
            conn = await asyncpg.connect(config['admin']['PSQL'])
            fetched = await conn.fetch('''SELECT sell_for FROM userdata.shopItems WHERE item_name = $1''',self.item_name)
            await conn.close()
            return dict(fetched[0])["sell_for"] if fetched else False
          
          
        async def gain(self):
            conn = await asyncpg.connect(config['admin']['PSQL'])
            fetched = await conn.fetch('''SELECT gain FROM userdata.shopItems WHERE item_name = $1''',self.item_name)
            await conn.close()
            return dict(fetched[0])["gain"] if fetched else None
        
        
        async def price(self, pp=None):
            conn = await asyncpg.connect(config['admin']['PSQL'])
            fetched = await conn.fetch('''SELECT multiplierDependent FROM userdata.shopItems WHERE item_name = $1''',self.item_name)
            await conn.close()
            #price = await self.default_price()*await pp.multiplier() if dict(fetched[0])["multiplierDependent"] else await self.default_price()
            return await self.default_price()*await pp.multiplier() if dict(fetched[0])["multiplierdependent"] else await self.default_price()
        
        
        async def add(self,item_type:str,item_desc:str,default_price:int,multiplierDependant:bool=False):
            conn = await asyncpg.connect(config['admin']['PSQL'])
            await conn.execute('''
                INSERT INTO userdata.shopItems(item_name, item_type, item_desc, default_price, multiplierDependent) VALUES($1, $2, $3, $4, $5)
                ON CONFLICT (item_name) DO NOTHING;
            ''',self.item_name,item_type,item_desc,default_price,multiplierDependant) #example: self.item_name,"TOOL","Perfect for fishing pps",250,False)
            return await conn.close()

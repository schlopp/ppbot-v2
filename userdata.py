import asyncpg
import discord
import random
import toml
from discord.ext import commands

with open("config.toml") as f:
    config = toml.loads(f.read())

class SQLMethodError(Exception):
    """SQL Method Error"""
    
    def __init__(self, method):
        self.method = method
        super().__init__('SQL Method unkown')
    
    def __str__(self):
        return f'\033[91mSQL Method: "{self.method}" unknown\033[0m'

async def printfetch(pgselect:str,pgfrom:str,pgwhere:str=None):
    """prints the return value of a fetched premade-sql statement\n\n__\n\nsql statement:\n\n- `SELECT {pgselect} FROM {pgfrom}( WHERE {pgwhere}; || ;  )`"""
    pgwhere = ";" if pgwhere == None else f" WHERE {pgwhere};"
    conn = await asyncpg.connect(config['admin']['PSQL'])
    fetched = await conn.fetch(
        f'''
        SELECT {pgselect} FROM {pgfrom}{pgwhere}
        '''
        )
    for i in fetched:
        print(dict(i))
    return await conn.close()

async def fetch(pgselect:str,pgfrom:str,pgwhere:str=None):
    """returns the return value of a fetched premade-sql statement\n\n__\n\nsql statement:\n\n- `SELECT {pgselect} FROM {pgfrom}( WHERE {pgwhere}; || ;  )`"""
    pgwhere = " WHERE {pgwhere};" if pgwhere else f";"
    conn = await asyncpg.connect('postgres://postgres:MPIWL32531@localhost:3626/ppbot')
    fetched = await conn.fetch(
        f'''
        SELECT {pgselect} FROM {pgfrom}{pgwhere}
        '''
        )
    await conn.close()
    return [dict(i) for i in fetched]

async def runsql(method:str,sqlstring:str):
    conn = await asyncpg.connect(config['admin']['PSQL'])
    if method == "execute":
        await conn.execute(sqlstring)
        return await conn.close()
    elif method == "fetch":
        fetched = await conn.fetch(sqlstring)
        await conn.close()
        return fetched
    else:
        await conn.close()
        raise SQLMethodError(method=method)
    
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
        self.user_id,       #$1 user_id
        "Unnamed Pp",       #$2 pp_name
        0,                  #$3 pp_size
        1)                  #$4 multiplier
        return await conn.close()
    
    
    
    async def delete(self):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            DELETE FROM userdata.pp WHERE user_id = $1 RETURNING *;
        ''',
        self.user_id)           #$1 user_id
        return await conn.close()
    
    
    
    async def size_add(self, amount:int):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            UPDATE userdata.pp SET pp_size = userdata.pp.pp_size + $2 WHERE userdata.pp.user_id = $1;
        ''',
        self.user_id,           #$1 user_id
        amount)                 #$2 pp_size
        return await conn.close()
    
    
    
    async def multiplier_add(self, amount:int):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            UPDATE userdata.pp SET multiplier = userdata.pp.multiplier + $2 WHERE userdata.pp.user_id = $1;
        ''',
        self.user_id,           #$1 user_id
        amount)                 #$2 pp_size
        return await conn.close()
    
    
    
    async def rename(self, pp_name:str):
        conn = await asyncpg.connect(config['admin']['PSQL'])
        await conn.execute('''
            UPDATE userdata.pp SET pp_name = $2 WHERE userdata.pp.user_id = $1;
        ''',
        self.user_id,           #$1 user_id
        pp_name)                #$2 pp_size
        return await conn.close()
    
    
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
    
    
    
    async def new_item(self, item_name:str, amount:int):
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

class Shop:
    def __init__(self):
        """e""" 
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

async def create_embed(ctx:commands.Context, **kwargs):
    """
    kwargs:
    user - `discord.Member` (default discord.ext.commands.Context)\n
    return_user - `bool` (default False)\n
    include_tip - `bool` (default True)\n
    pp_dependent - `bool` (default True)\n
    pp_adjective - `bool` (default False)\n
    item_required - `String | None` (default None)\n
    """
    embed:discord.Embed = discord.Embed(colour=discord.Colour(random.choice([0x008000, 0xffa500, 0xffff00])))
    user = kwargs.get('user', ctx.author)
    return_user:bool = kwargs.get('return_user',False)
    include_tip:bool = kwargs.get('include_tip',True)
    pp_dependent:bool = kwargs.get('pp_dependent',True)
    pp_adjective:bool = kwargs.get('pp_adjective',False)
    item_required = kwargs.get('item_required',None)
    usercheck = user == ctx.author
    pp = Pp(user.id)
    check = await pp.check()
    
    
    exception = None
    if pp_dependent and not check:
            exception = f"{user.mention}, you need a pp first! Get one using `pp new`!" if usercheck else "that person doesnt have a cock. (might be a trap)"
    if pp_adjective and check:
            exception = f"{user.mention}, you already have a pp :("
    if item_required:
        inv = Inv(user.id)
        if not await inv.has_item(item_required):
            exception = f'you need a "{item_required}" to use this command. Check if its for sale at the shop!'
    if include_tip and random.randint(1,3)==2:
        embed.add_field(name="TIP:",value=random.choice([
            "Tools in the shop unlock commands!",
            "There's a small chance of an event happening upon using a command!",
            #"You can see the leaderboard by using the 'pp leaderboard' command!",
            "There are a ton of fun commands! Have you tried them yet?",
            "Invite my friend's bot! discord.ly/ghigeon",
            "Join the official pp bot server! use `pp support`",
            "Add pp bot to your server! use `pp invite`"
        ]))
    if return_user:
        return embed,pp,user,exception
    return embed,pp,exception

async def handle_exception(ctx:commands.Context, exception:str):
    embed = discord.Embed(colour=discord.Colour(0xff0000))
    embed.title = f"Oopsie {ctx.author.display_name}, something went wrong."
    embed.description = exception
    return await ctx.send(embed=embed)

import asyncpg
import toml

with open("../config.toml") as f:
    config = toml.loads(f.read())

class SQLMethodError(Exception):
    """SQL Method Error"""
    
    def __init__(self, method):
        self.method = method
        super().__init__('SQL Method unkown')
    
    def __str__(self):
        return f'SQL Method: "{self.method}" unknown\033[0m'


async def fetch(pgselect:str,pgfrom:str,pgwhere:str=None):
    """returns the return value of a fetched premade-sql statement\n\n__\n\nsql statement:\n\n- `SELECT {pgselect} FROM {pgfrom}( WHERE {pgwhere}; || ;  )`"""
    pgwhere = " WHERE {pgwhere};" if pgwhere else f";"
    conn = await asyncpg.connect(config['admin']['PSQL'])
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

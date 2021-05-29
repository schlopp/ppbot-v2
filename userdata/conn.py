import asyncpg
import toml

with open("./config.toml") as f:
    config = toml.loads(f.read())

class DatabaseConnection:
    """
    Database Connection go brr
    """
    def __init__(self, conn=None):
        self.conn = conn

    async def connect(self):
        self.conn = await asyncpg.connect(config['admin']['PSQL'])

    async def disconnect(self):
        await self.conn.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.disconnect()

    async def __call__(self, sql, *args):
        
        return await self.conn.fetch(sql, *args)
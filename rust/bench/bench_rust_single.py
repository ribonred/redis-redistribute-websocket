import asyncio
import uvloop
import redisrust
from tqdm.asyncio import tqdm

uvloop.install()

async def main():
    pool = await redisrust.create_pool("redis://localhost", 10, 0)
    async for i in tqdm(range(1000000), desc="Setting keys..."):
        await pool.set("bench", "yes")


asyncio.run(main())

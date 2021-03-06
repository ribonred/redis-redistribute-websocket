import asyncio
import uvloop
import redisrust
from tqdm.asyncio import tqdm

uvloop.install()

async def main():
    pool = await redisrust.create_pool("redis://localhost", 10, 0)
    futures = []
    async for i in tqdm(range(1000000), desc="Bulk spawning..."):
        futures.append(pool.set(f"bench{i}", "yes"))
    await asyncio.gather(*futures)


asyncio.run(main())

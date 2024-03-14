import asyncio
import time

async def run():
    while True:
        await asyncio.sleep(1)
        print(time.localtime())

loop = asyncio.get_event_loop()
tasks = [
    loop.create_task(run()),
]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
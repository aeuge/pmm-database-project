import asyncio
import random


async def publicate(conn):
    while True:
        category = random.choice(['esse', 'publication', 'report', 'interview'])
        print(f'Publicate {category}')
        await asyncio.sleep(random.randrange(5, 10) / 10)


async def comment(conn):
    while True:
        print(f'Comment')
        await asyncio.sleep(random.randrange(1, 2) / 10)


async def start():
    t1 = asyncio.create_task(publicate(1))
    t2 = asyncio.create_task(comment(1))
    await t1
    await t2


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        pass

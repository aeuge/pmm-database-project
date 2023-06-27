import asyncio
import uuid
from datetime import datetime
import random
import asyncpg
from faker import Faker

from loads.dyn_loads import gen_cinema_movie_presence

fake = Faker()
ru_fake = Faker('ru_RU')


async def create_publication(dsn):
    conn = await asyncpg.connect(dsn)
    with await conn.cursor() as cursor:
        # get users ids
        await cursor.execute('SELECT id FROM users;')
        users_ids = [id[0] for id in await cursor.fetchall()]
        # get publication category ids
        await cursor.execute('SELECT id FROM publications_category;')
        publications_category_ids = [id[0] for id in await cursor.fetchall()]
        while True:
            user_id = random.choice(users_ids)
            category_id = random.choice(publications_category_ids)
            print('Action: create publication')
            sql = 'INSERT INTO publications (title, text, author, category, changed_at) VALUES (%s, %s, %s, %s, %s);'
            await cursor.execute(sql, (
                ru_fake.sentence(nb_words=5),
                ru_fake.paragraph(nb_sentences=500, variable_nb_sentences=True),
                random.choice(users_ids),
                random.choice(publications_category_ids),
                None,
                ))
            await conn.commit()
            await asyncio.sleep(random.randrange(2, 5))


async def update_publication(dsn):
    conn = await asyncpg.connect(dsn)
    with await conn.cursor() as cursor:
        while True:
            await cursor.execute('SELECT id FROM publications;')
            publications_ids = [id[0] for id in await cursor.fetchall()]
            publication_id = random.choice(publications_ids)
            print(f'Action: update publication ({publication_id})')
            sql = 'UPDATE publications SET "text" = %s, changed_at = %s WHERE id = %s;'
            await cursor.execute(sql, (
                ru_fake.paragraph(nb_sentences=500, variable_nb_sentences=True),
                datetime.now(),
                publication_id,
                ))
            await conn.commit()
            await asyncio.sleep(random.randrange(1, 3))


async def create_comment_movie(dsn):
    conn = await asyncpg.connect(dsn)
    with await conn.cursor() as cursor:
        # get users ids
        await cursor.execute('SELECT id FROM users;')
        users_ids = [id[0] for id in await cursor.fetchall()]
        # get movies ids
        await cursor.execute('SELECT id FROM movies;')
        movies_ids = [id[0] for id in await cursor.fetchall()]

        while True:
            is_child = fake.boolean(chance_of_getting_true=25)
            if is_child:
                await cursor.execute('SELECT id FROM comments where publication_id is NULL;')
                comments_ids = [id[0] for id in await cursor.fetchall()]
                parent_id = random.choice(comments_ids)
                await cursor.execute('SELECT movie_id FROM comments where id = %s;', (parent_id,))
                movie_id = cursor.fetchone()
            else:
                parent_id = None
                movie_id = random.choice(movies_ids)

            print(f'Action: create comment_movie (child={is_child})')
            sql = 'INSERT INTO comments (user_id, "comment", parent_id, movie_id, publication_id, changed_at) VALUES ' \
                  '(%s, %s, %s, %s, %s, %s);'
            await cursor.execute(sql, (
                random.choice(users_ids),
                ru_fake.sentence(nb_words=15),
                parent_id,
                movie_id,
                None,
                None,
                ))
            await conn.commit()
            await asyncio.sleep(random.randrange(5, 30) / 10)


async def create_comment_publication(dsn):
    conn = await asyncpg.connect(dsn)
    with await conn.cursor() as cursor:
        # get users ids
        await cursor.execute('SELECT id FROM users;')
        users_ids = [id[0] for id in await cursor.fetchall()]
        # get movies ids
        await cursor.execute('SELECT id FROM publications;')
        publications_ids = [id[0] for id in await cursor.fetchall()]

        while True:
            is_child = fake.boolean(chance_of_getting_true=25)
            if is_child:
                await cursor.execute('SELECT id FROM comments where movie_id is NULL;')
                comments_ids = [id[0] for id in await cursor.fetchall()]
                parent_id = random.choice(comments_ids)
                await cursor.execute('SELECT publication_id FROM comments where id = %s;', (parent_id,))
                publication_id = cursor.fetchone()
            else:
                parent_id = None
                publication_id = random.choice(publications_ids)

            print(f'Action: create comment_movie (child={is_child})')
            sql = 'INSERT INTO comments (user_id, "comment", parent_id, movie_id, publication_id, changed_at) VALUES ' \
                  '(%s, %s, %s, %s, %s, %s);'
            await cursor.execute(sql, (
                random.choice(users_ids),
                ru_fake.sentence(nb_words=15),
                parent_id,
                None,
                publication_id,
                None,
                ))
            await conn.commit()
            await asyncio.sleep(random.randrange(1, 30) / 10)


async def update_cinema_online_movie_presence(dsn):
    """"""
    async def async_gen_cinema_movie_presence(conn, count):
        """"""
        with conn.cursor() as cursor:
            await cursor.execute('SELECT id FROM movies;')
            movies_id_list = [id[0] for id in cursor.fetchall()]

            await cursor.execute('SELECT id FROM cinema_online;')
            cinema_online_id_list = [id[0] for id in cursor.fetchall()]
            data = []
            for cinema_id in range(count):
                data.append({
                    'movie_id': random.choice(movies_id_list),
                    'cinema_id': random.choice(cinema_online_id_list),
                    'price': fake.random_sample(elements=(100, 150, 200, 250, 300, 350, 400, 450), length=1)[0],
                    'rating': fake.random_sample(elements=(1, 2, 3, 4, 5), length=1)[0],
                    'discount': fake.random_sample(elements=(10, 20, 30, 40, 50), length=1)[0],
                    'view_count': fake.random_number(digits=7, fix_len=False),
                    'last_update': fake.past_datetime(),
                    })
            return data

    conn = await asyncpg.connect(dsn)
    with await conn.cursor() as cursor:
        while True:
            # delete some presence
            print('Action: delete some movie presence')
            await asyncio.sleep(random.randrange(3, 7))
            await cursor.execute('with p as (select id from cinema_online_movie_presence ORDER BY last_update LIMIT %s) '
                                 'delete from cinema_online_movie_presence where id in (select id from p);',
                                 (random.randrange(3, 5)))

            # insert new some presence
            print('Action: add some new movie presence')
            statement = r'INSERT INTO cinema_online_movie_presence (movie_id, cinema_id, price, rating, discount, view_count, last_update' \
                        r') VALUES (%s,%s,%s,%s,%s,%s,%s);'

            new_presence_count = random.randrange(4, 7)
            for row in await async_gen_cinema_movie_presence(conn, new_presence_count):
                async with conn:
                    try:
                        print("INSERT presence: ", row)
                        await cursor.execute(statement, (row['movie_id'],
                                                   row['cinema_id'],
                                                   row['price'],
                                                   row['rating'],
                                                   row['discount'],
                                                   row['view_count'],
                                                   row['last_update'],
                                                   )
                                       )
                    except Exception:
                        pass
            conn.commit()


async def create_user_movie_order(dsn):
    conn = await asyncpg.connect(dsn)
    with await conn.cursor() as cursor:
        # get cinema_online ids
        await cursor.execute('SELECT id FROM cinema_online;')
        cinema_online_ids = [id[0] for id in await cursor.fetchall()]
        # get movies ids
        await cursor.execute('SELECT id FROM movies;')
        movies_ids = [id[0] for id in await cursor.fetchall()]
        # get users ids
        cursor.execute('SELECT id FROM users;')
        users_ids = [id[0] for id in cursor.fetchall()]
        sql = 'INSERT INTO user_movie_orders (cinema_order_id, movie_id, user_id, online_cinema_id, price, "date") VALUES ' \
              '(%s, %s, %s, %s, %s, %s);'

        while True:
            print('Action: create user movie order')
            await cursor.execute(sql, (
                str(uuid.uuid4()),
                random.choice(movies_ids),
                random.choice(users_ids),
                random.choice(cinema_online_ids),
                fake.random_sample(elements=(100, 150, 200, 250, 300, 350, 400, 450), length=1)[0],
                datetime.now(),
                ))
            await conn.commit()
            await asyncio.sleep(random.randrange(3, 30) / 10)


async def set_user_rating_movie(dsn):
    conn = await asyncpg.connect(dsn)
    with await conn.cursor() as cursor:
        # get movies ids
        await cursor.execute('SELECT id FROM movies;')
        movies_ids = [id[0] for id in await cursor.fetchall()]
        # get users ids
        cursor.execute('SELECT id FROM users;')
        users_ids = [id[0] for id in cursor.fetchall()]
        sql = r'INSERT INTO users_rating (rating, user_id, movie_id, publication_id, created_at) VALUES (%s,%s,%s,%s,%s);'

        while True:
            print('Action: set user movie rating')
            await cursor.execute(sql, (
                fake.random_sample(elements=(1, 2, 3, 4, 5), length=1)[0],
                random.choice(users_ids),
                random.choice(movies_ids),
                None,
                datetime.now(),
                ))
            await conn.commit()
            await asyncio.sleep(random.randrange(1, 3))


async def set_user_rating_publication(dsn):
    conn = await asyncpg.connect(dsn)
    with await conn.cursor() as cursor:
        # get users ids
        cursor.execute('SELECT id FROM users;')
        users_ids = [id[0] for id in cursor.fetchall()]
        sql = r'INSERT INTO users_rating (rating, user_id, movie_id, publication_id, created_at) VALUES (%s,%s,%s,%s,%s);'

        while True:
            await cursor.execute('SELECT id FROM publications;')
            publications_ids = [id[0] for id in await cursor.fetchall()]
            print('Action: set user publication rating')
            await cursor.execute(sql, (
                fake.random_sample(elements=(1, 2, 3, 4, 5), length=1)[0],
                random.choice(users_ids),
                None,
                random.choice(publications_ids),
                datetime.now(),
                ))
            await conn.commit()
            await asyncio.sleep(random.randrange(1, 3))


async def start():
    dsn = 'postgresql://postgres:POSTGRES6602!@10.66.2.134:5432/kinoteka?sslmode=require'
    t1 = asyncio.create_task(create_publication(dsn))
    t2 = asyncio.create_task(update_publication(dsn))
    t3 = asyncio.create_task(create_comment_movie(dsn))
    t4 = asyncio.create_task(create_comment_publication(dsn))
    t5 = asyncio.create_task(update_cinema_online_movie_presence(dsn))
    t6 = asyncio.create_task(create_user_movie_order(dsn))
    t7 = asyncio.create_task(set_user_rating_movie(dsn))
    t8 = asyncio.create_task(set_user_rating_publication(dsn))

    await t1
    await t2
    await t3
    await t4
    await t5
    await t6
    await t7
    await t8


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        pass

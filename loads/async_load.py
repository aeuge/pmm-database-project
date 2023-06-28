import asyncio
import random
import uuid
from datetime import datetime

import asyncpg
from faker import Faker

from stat_loads import domains_list

fake = Faker()
ru_fake = Faker('ru_RU')


SQL_SELECT_USERS_IDS = 'SELECT id FROM users WHERE deleted_at IS NULL;'
SQL_SELECT_PUB_CAT_IDS = 'SELECT id FROM publications_category;'
SQL_CREATE_USER = 'INSERT INTO users (username, email, "password", fio, bio, created_at, birthday) VALUES ($1, $2, $3, $4, $5, $6, $7);'
SQL_DELETE_USER = 'UPDATE users SET deleted_at = $1 WHERE id = $2;'
SQL_SELECT_PUBLICATION_IDS = 'SELECT id FROM publications;'
SQL_CREATE_PUBLICATION = 'INSERT INTO publications (title, "text", author, "category") VALUES ($1, $2, $3, $4);'
SQL_UPDATE_PUBLICATION = 'UPDATE publications SET "text" = $1, changed_at = $2 WHERE id = $3;'
SQL_DELETE_PUBLICATION = 'DELETE FROM publications WHERE id = $1;'
SQL_SELECT_MOVIE_IDS = 'SELECT id FROM movies;'
SQL_CREATE_COMMENT_MOVIE = 'INSERT INTO comments (user_id, "comment", parent_id, movie_id) VALUES  ($1, $2, $3, $4);'
SQL_CREATE_COMMENT_PUBLICATION = 'INSERT INTO comments (user_id, "comment", parent_id, publication_id) VALUES  ($1, $2, $3, $4);'
SQL_SELECT_CINEMA_ONLINE_IDS = 'SELECT id FROM cinema_online;'


async def create_user(dsn):
    conn = await asyncpg.connect(dsn)
    stmt = await conn.prepare(SQL_CREATE_USER)
    while True:
        print('Action: create user')
        await stmt.fetch(ru_fake.user_name(),
                         ru_fake.email(domain=random.choice(domains_list)),
                         str(uuid.uuid4()),
                         ru_fake.name(),
                         ' '.join(ru_fake.sentences(nb=5)),
                         datetime.now(),
                         ru_fake.date_of_birth(minimum_age=17, maximum_age=60),  # birthday
                         )
        await asyncio.sleep(random.randrange(1, 5))


async def delete_user(dsn):
    conn = await asyncpg.connect(dsn)
    # get publication category ids
    stmt = await conn.prepare(SQL_DELETE_USER)
    while True:
        users_ids = [id[0] for id in await conn.fetch(SQL_SELECT_USERS_IDS)]
        user_id = random.choice(users_ids)
        print('Action: delete user (mark)')
        try:
            await stmt.fetch(datetime.now(),
                             user_id)
        except Exception:
            pass
        await asyncio.sleep(random.randrange(1, 10))


async def create_publication(dsn):
    conn = await asyncpg.connect(dsn)
    publications_category_ids = [id[0] for id in await conn.fetch(SQL_SELECT_PUB_CAT_IDS)]
    stmt = await conn.prepare(SQL_CREATE_PUBLICATION)
    while True:
        # get publication category ids
        users_ids = [id[0] for id in await conn.fetch(SQL_SELECT_USERS_IDS)]
        user_id = random.choice(users_ids)
        category_id = random.choice(publications_category_ids)
        print('Action: create publication')
        await stmt.fetch(ru_fake.sentence(nb_words=5),
                         ru_fake.paragraph(nb_sentences=500, variable_nb_sentences=True),
                         user_id,
                         category_id,
                         )
        await asyncio.sleep(random.randrange(1, 5))


async def update_publication(dsn):
    conn = await asyncpg.connect(dsn)
    stmt = await conn.prepare(SQL_UPDATE_PUBLICATION)
    while True:
        publications_ids = [id[0] for id in await conn.fetch(SQL_SELECT_PUBLICATION_IDS)]
        publication_id = random.choice(publications_ids)
        print(f'Action: update publication ({publication_id})')
        await stmt.fetch(ru_fake.paragraph(nb_sentences=500, variable_nb_sentences=True),
                         datetime.now(),
                         publication_id,
                         )
        await asyncio.sleep(random.randrange(1, 3))


async def delete_publication(dsn):
    conn = await asyncpg.connect(dsn)
    stmt = await conn.prepare(SQL_DELETE_PUBLICATION)
    while True:
        await asyncio.sleep(random.randrange(1, 10))
        publications_ids = [id[0] for id in await conn.fetch(SQL_SELECT_PUBLICATION_IDS)]
        publication_id = random.choice(publications_ids)
        print(f'Action: delete publication ({publication_id})')
        await stmt.fetch(publication_id)


async def create_comment_movie(dsn):
    conn = await asyncpg.connect(dsn)
    stmt = await conn.prepare(SQL_CREATE_COMMENT_MOVIE)
    # get users ids
    users_ids = [id[0] for id in await conn.fetch(SQL_SELECT_USERS_IDS)]
    # get movies ids
    movies_ids = [id[0] for id in await conn.fetch(SQL_SELECT_MOVIE_IDS)]

    while True:
        async with conn.transaction():
            is_child = fake.boolean(chance_of_getting_true=25)
            if is_child:
                comments_ids = [id[0] for id in
                                await conn.fetch('SELECT id FROM comments WHERE publication_id IS NULL;')]
                parent_id = random.choice(comments_ids)
                movie_id = await conn.fetchval('SELECT movie_id FROM comments WHERE id = $1;', parent_id)
            else:
                parent_id = None
                movie_id = random.choice(movies_ids)

            print(f'Action: create comment movie (child={is_child})')
            await stmt.fetch(random.choice(users_ids),
                             ru_fake.sentence(nb_words=15),
                             parent_id,
                             movie_id,
                             )
        await asyncio.sleep(random.randrange(2, 10) / 50)


async def create_comment_publication(dsn):
    conn = await asyncpg.connect(dsn)
    stmt = await conn.prepare(SQL_CREATE_COMMENT_PUBLICATION)
    # get users ids
    users_ids = [id[0] for id in await conn.fetch(SQL_SELECT_USERS_IDS)]
    # get movies ids
    publications_ids = [id[0] for id in await conn.fetch(SQL_SELECT_PUBLICATION_IDS)]

    while True:
        async with conn.transaction():
            is_child = fake.boolean(chance_of_getting_true=25)
            if is_child:
                comments_ids = [id[0] for id in
                                await conn.fetch('SELECT id FROM comments WHERE movie_id IS NULL;')]
                parent_id = random.choice(comments_ids)
                publication_id = await conn.fetchval('SELECT publication_id FROM comments WHERE id = $1;', parent_id)
            else:
                parent_id = None
                publication_id = random.choice(publications_ids)

            print(f'Action: create comment publication (child={is_child})')
            await stmt.fetch(random.choice(users_ids),
                             ru_fake.sentence(nb_words=15),
                             parent_id,
                             publication_id,
                             )
        await asyncio.sleep(random.randrange(2, 10) / 100)


async def update_cinema_online_movie_presence(dsn):
    """"""

    async def async_gen_cinema_movie_presence(count):
        data = []
        for cinema_id in range(count):
            data.append({
                'movie_id': random.choice(movies_id_list),
                'cinema_id': random.choice(cinema_online_id_list),
                'price': fake.random_sample(elements=(100, 150, 200, 250, 300, 350, 400, 450), length=1)[0],
                'rating': fake.random_sample(elements=(1, 2, 3, 4, 5), length=1)[0],
                'discount': fake.random_sample(elements=(10, 20, 30, 40, 50), length=1)[0],
                'view_count': fake.random_number(digits=7, fix_len=False),
                'last_update': datetime.now()
            })
        return data

    conn = await asyncpg.connect(dsn)
    movies_id_list = [id[0] for id in await conn.fetch(SQL_SELECT_MOVIE_IDS)]
    cinema_online_id_list = [id[0] for id in await conn.fetch(SQL_SELECT_CINEMA_ONLINE_IDS)]
    delete_stmt = await conn.prepare(
            'WITH p AS (SELECT id FROM cinema_online_movie_presence ORDER BY last_update LIMIT $1) '
            'DELETE FROM cinema_online_movie_presence WHERE id IN (SELECT id FROM p);')
    insert_stmt = await conn.prepare(
            'INSERT INTO cinema_online_movie_presence (movie_id, cinema_id, price, rating, discount, view_count, last_update' \
            ') VALUES ($1,$2,$3,$4,$5,$6,$7);')

    while True:
        # delete some presence
        await asyncio.sleep(random.randrange(3, 7))
        delete_count = random.randrange(2, 5)
        print(f'Action: delete some movie presence (count={delete_count})')
        await delete_stmt.fetch(delete_count)

        # insert new some presence
        new_presence_count = random.randrange(2, 5)
        print(f'Action: add some new movie presence (count={new_presence_count})')
        for row in await async_gen_cinema_movie_presence(new_presence_count):
            async with conn.transaction():
                try:
                    await insert_stmt.fetch(row['movie_id'],
                                            row['cinema_id'],
                                            row['price'],
                                            row['rating'],
                                            row['discount'],
                                            row['view_count'],
                                            row['last_update'],
                                            )
                except Exception:
                    pass


async def create_user_movie_order(dsn):
    conn = await asyncpg.connect(dsn)
    # get cinema_online ids
    cinema_online_ids = [id[0] for id in await conn.fetch(SQL_SELECT_CINEMA_ONLINE_IDS)]
    # get movies ids
    movies_ids = [id[0] for id in await conn.fetch(SQL_SELECT_MOVIE_IDS)]
    # get users ids
    users_ids = [id[0] for id in await conn.fetch(SQL_SELECT_USERS_IDS)]
    stmt = await conn.prepare(
            'INSERT INTO user_movie_orders (cinema_order_id, movie_id, user_id, online_cinema_id, price, "date") VALUES ' \
            '($1, $2, $3, $4, $5, $6);')

    while True:
        async with conn.transaction():
            try:
                print('Action: create user movie order')
                await stmt.fetch(
                        str(uuid.uuid4()),
                        random.choice(movies_ids),
                        random.choice(users_ids),
                        random.choice(cinema_online_ids),
                        fake.random_sample(elements=(100, 150, 200, 250, 300, 350, 400, 450), length=1)[0],
                        datetime.now(),
                )
            except Exception:
                pass
        await asyncio.sleep(random.randrange(5, 50) / 100)


async def set_user_rating_movie(dsn):
    conn = await asyncpg.connect(dsn)
    # get movies ids
    movies_ids = [id[0] for id in await conn.fetch(SQL_SELECT_MOVIE_IDS)]
    # get users ids
    users_ids = [id[0] for id in await conn.fetch(SQL_SELECT_USERS_IDS)]
    stmt = await conn.prepare('INSERT INTO users_rating (rating, user_id, movie_id, created_at) VALUES ($1,$2,$3,$4);')

    while True:
        async with conn.transaction():
            try:
                print('Action: set user rating on movie')
                await stmt.fetch(
                        fake.random_sample(elements=(1, 2, 3, 4, 5), length=1)[0],
                        random.choice(users_ids),
                        random.choice(movies_ids),
                        datetime.now(),
                )
            except Exception:
                pass
        await asyncio.sleep(random.randrange(2, 10) / 50)


async def set_user_rating_publication(dsn):
    conn = await asyncpg.connect(dsn)
    # get publications ids
    publications_ids = [id[0] for id in await conn.fetch(SQL_SELECT_PUBLICATION_IDS)]
    # get users ids
    users_ids = [id[0] for id in await conn.fetch(SQL_SELECT_USERS_IDS)]
    stmt = await conn.prepare(
            'INSERT INTO users_rating (rating, user_id, publication_id, created_at) VALUES ($1,$2,$3,$4);'
    )

    while True:
        async with conn.transaction():
            try:
                print('Action: set user rating on publication')
                await stmt.fetch(
                        fake.random_sample(elements=(1, 2, 3, 4, 5), length=1)[0],
                        random.choice(users_ids),
                        random.choice(publications_ids),
                        datetime.now(),
                )
            except Exception:
                pass
        await asyncio.sleep(random.randrange(2, 10) / 50)


async def start():
    dsn = 'postgresql://postgres:POSTGRES6602!@10.66.2.134:5432/kinoteka?sslmode=require'
    # dsn = 'postgresql://postgres:POSTGRESQLHOME@nas:5432/kinoteka?sslmode=require'
    task_list = [
        asyncio.create_task(create_user(dsn)),
        asyncio.create_task(delete_user(dsn)),
        asyncio.create_task(create_publication(dsn)),
        asyncio.create_task(update_publication(dsn)),
        asyncio.create_task(delete_publication(dsn)),
        asyncio.create_task(create_comment_movie(dsn)),
        asyncio.create_task(create_comment_publication(dsn)),
        asyncio.create_task(update_cinema_online_movie_presence(dsn)),
        asyncio.create_task(create_user_movie_order(dsn)),
        asyncio.create_task(set_user_rating_movie(dsn)),
        asyncio.create_task(set_user_rating_publication(dsn)),
    ]

    for task in task_list:
        await task


if __name__ == '__main__':
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        pass

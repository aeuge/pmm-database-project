import random
import uuid

from faker import Faker

fake = Faker()
ru_fake = Faker('ru_RU')


def gen_awards(conn, procent=0.5):
    """"""
    with conn.cursor() as main_cursor, conn.cursor() as sub_cursor:
        main_cursor.execute('SELECT id FROM film_award_registry;')
        film_awards_id_list = [id[0] for id in main_cursor.fetchall()]

        main_cursor.execute('SELECT id FROM film_award_nominations_registry;')
        film_awards_nomination_id_list = [id[0] for id in main_cursor.fetchall()]

        main_cursor.execute('SELECT id FROM movies ORDER BY title;')
        movie_count = int(main_cursor.rowcount * procent)
        movies_list = [id[0] for id in main_cursor.fetchall()]

        for _ in range(movie_count):
            id = random.choice(movies_list)
            sub_cursor.execute('SELECT person_id FROM movie_staff_m2m WHERE movie_id = %s;', (id,))
            for _ in range(sub_cursor.rowcount):
                yield {
                    'film_award_id': random.choice(film_awards_id_list),
                    'movie_id': id,
                    'person_id': sub_cursor.fetchone(),
                    'nomination_id': random.choice(film_awards_nomination_id_list),
                }


def gen_cinema_movie_presence(conn, count=100):
    """"""
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM movies ORDER BY title LIMIT %s;', (count,))
        movies_id_list = [id[0] for id in cursor.fetchall()]

        cursor.execute('SELECT id FROM cinema_online;')
        cinema_online_id_list = [id[0] for id in cursor.fetchall()]

        for cinema_id in cinema_online_id_list:
            yield {
                'movie_id': random.choice(movies_id_list),
                'cinema_id': cinema_id,
                'price': fake.random_sample(elements=(100, 150, 200, 250, 300, 350, 400, 450), length=1)[0],
                'rating': fake.random_sample(elements=(1, 2, 3, 4, 5), length=1)[0],
                'discount': fake.random_sample(elements=(10, 20, 30, 40, 50), length=1)[0],
                'view_count': fake.random_number(digits=7, fix_len=False),
                'last_update': fake.past_datetime(),
            }


def gen_user_movie_orders(conn, count=100):
    """"""
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM cinema_online;')
        cinema_online_id_list = [id[0] for id in cursor.fetchall()]

        cursor.execute('SELECT id FROM movies ORDER BY title LIMIT %s;', (count,))
        movies_id_list = [id[0] for id in cursor.fetchall()]

        cursor.execute('SELECT id FROM users ORDER BY username LIMIT %s;', (count,))
        users_id_list = [id[0] for id in cursor.fetchall()]

        for movie_id in movies_id_list:
            yield {
                'cinema_order_id': str(uuid.uuid4()),
                'movie_id': movie_id,
                'user_id': random.choice(users_id_list),
                'online_cinema_id': random.choice(cinema_online_id_list),
                'price': fake.random_sample(elements=(100, 150, 200, 250, 300, 350, 400, 450), length=1)[0],
                'date': fake.past_datetime('-5y'),
            }


def gen_publications(conn, count=100):
    """"""
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM publications_category;')
        publications_category_id_list = [id[0] for id in cursor.fetchall()]

        cursor.execute('SELECT id FROM users LIMIT %s;', (count,))
        users_id_list = [id[0] for id in cursor.fetchall()]

        for _ in range(count):
            yield {
                'title': ru_fake.sentence(nb_words=5),
                'text': ru_fake.paragraph(nb_sentences=500, variable_nb_sentences=True),
                'author': random.choice(users_id_list),
                'category': random.choice(publications_category_id_list),
                'created_at': fake.past_datetime('-5y'),
                'changed_at': fake.past_datetime('-5y'),
            }


def gen_users_rating(conn, count=100):
    """"""
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM users LIMIT %s;', (count,))
        users_id_list = [id[0] for id in cursor.fetchall()]

        cursor.execute('SELECT id FROM movies ORDER BY title LIMIT %s;', (count,))
        movies_id_list = [id[0] for id in cursor.fetchall()]

        cursor.execute('SELECT id FROM publications ORDER BY title LIMIT %s;', (count,))
        publications_id_list = [id[0] for id in cursor.fetchall()]

        for _ in range(count):
            set_movie = set_publication = False
            rtype = fake.boolean(chance_of_getting_true=50)
            if rtype:
                set_movie = True
            else:
                set_publication = True

            yield {
                'user_id': random.choice(users_id_list),
                'rating': fake.random_sample(elements=(1, 2, 3, 4, 5), length=1)[0],
                'movie_id': random.choice(movies_id_list) if set_movie else None,
                'publication_id': random.choice(publications_id_list) if set_publication else None,
                'created_at': fake.past_datetime('-5y'),
            }


def gen_comments(conn, count=100):
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM users LIMIT %s;', (count,))
        users_id_list = [id[0] for id in cursor.fetchall()]

        cursor.execute('SELECT id FROM movies ORDER BY title LIMIT %s;', (count,))
        movies_id_list = [id[0] for id in cursor.fetchall()]

        cursor.execute('SELECT id FROM publications ORDER BY title LIMIT %s;', (count,))
        publications_id_list = [id[0] for id in cursor.fetchall()]

        for _ in range(count):
            set_movie = set_publication = False
            rtype = fake.boolean(chance_of_getting_true=50)
            if rtype:
                set_movie = True
            else:
                set_publication = True

            yield {
                'user_id': random.choice(users_id_list),
                'comment': ru_fake.sentence(nb_words=25),
                'parent_id': None,  # todo add parent id random
                'movie_id': random.choice(movies_id_list) if set_movie else None,
                'publication_id': random.choice(publications_id_list) if set_publication else None,
                'created_at': fake.past_datetime('-5y'),
                'changed_at': fake.past_datetime('-5y'),
            }

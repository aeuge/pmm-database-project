import psycopg2

from dyn_loads import (gen_awards, gen_cinema_movie_presence, gen_comments, gen_movies_staff, gen_publications,
                             gen_user_movie_orders, gen_users_rating)
from stat_loads import (gen_awards_category, gen_awards_nominations, gen_cinema_online, gen_movies_data,
                        gen_person_data, gen_persons_positions, gen_publications_category, gen_tags_list,
                        gen_users_data)


# Заплнение статическими данными
def load_tags(conn, cursor):
    # tags
    print('load_tags..', end='')
    statement = r"INSERT INTO tags (title) VALUES (%s);"
    for tag in gen_tags_list():
        cursor.execute(statement, (tag,))
    print('OK')


def load_publications_category(conn, cursor):
    # tags
    print('load_publications_category..', end='')
    statement = r"INSERT INTO publications_category (title) VALUES (%s);"
    for publications_category in gen_publications_category():
        cursor.execute(statement, (publications_category,))
    print('OK')


def load_award_registry(conn, cursor):
    # tags
    print('load_award_registry..', end='')
    statement = r"INSERT INTO film_award_registry (title) VALUES (%s);"
    for award in gen_awards_category():
        cursor.execute(statement, (award,))
    print('OK')


def load_awards_nominations(conn, cursor):
    # tags
    print('load_awards_nominations..', end='')
    statement = r"INSERT INTO film_award_nominations_registry (title) VALUES (%s);"
    for nomination in gen_awards_nominations():
        cursor.execute(statement, (nomination,))
    print('OK')


def load_persons_positions(conn, cursor):
    # tags
    print('load_persons_positions..', end='')
    statement = r"INSERT INTO person_position (title) VALUES (%s);"
    for position in gen_persons_positions():
        cursor.execute(statement, (position,))
    print('OK')


def load_cinema_online(conn, cursor):
    # tags
    print('load_cinema_online..', end='')
    statement = r"INSERT INTO cinema_online (title, url) VALUES (%s,%s);"
    for row in gen_cinema_online():
        cursor.execute(statement, (row['title'],
                                   row['url']
                                   ))
    print('OK')


def load_persons(conn, cursor):
    # tags
    print('load_persons..', end='')
    statement = r"INSERT INTO persons (country, name, birthday, bio) VALUES (%s,%s,%s,%s);"
    for row in gen_person_data():
        cursor.execute(statement, (row['country'],
                                   row['name'],
                                   row['birthday'],
                                   row['bio'],
                                   )
                       )
    print('OK')


def load_users(conn, cursor):
    # tags
    print('load_users..', end='')
    statement = r'INSERT INTO users (username, email, "password", fio, bio, created_at, birthday, last_logon) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);'
    for row in gen_users_data(count=100):
        with conn:
            try:
                cursor.execute(statement, (row['username'],
                                           row['email'],
                                           row['password'],
                                           row['fio'],
                                           row['bio'],
                                           row['created_at'],
                                           row['birthday'],
                                           row['last_logon'],
                                           )
                               )
            except Exception:
                pass
    print('OK')


def load_movies_data(conn, cursor):
    # tags
    print('load_movies_data..', end='')
    statement = r'INSERT INTO movies (isbn, title, title_original, country, "year", budget, boxoffice, rating, duration, rars, tags, subject) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
    for row in gen_movies_data():
        cursor.execute(statement, (row['isbn'],
                                   row['title'],
                                   row['title_original'],
                                   row['country'],
                                   row['year'],
                                   row['budget'],
                                   row['boxoffice'],
                                   row['rating'],
                                   row['duration'],
                                   row['rars'],
                                   row['tags'],
                                   row['subject'],
                                   )
                       )
    print('OK')


# load dynamic data ----------------
def load_movies_staff(conn, cursor):
    """"""
    print('load_movies_staff..', end='')
    statement = r'INSERT INTO movie_staff_m2m (character, is_lead_role, position_id, person_id, movie_id) VALUES (%s,%s,%s,%s,%s);'
    for row in gen_movies_staff(conn):
        cursor.execute(statement, (row['character'],
                                   row['is_lead_role'],
                                   row['position_id'],
                                   row['person_id'],
                                   row['movie_id'],
                                   )
                       )
    print('OK')


def load_publications(conn, cursor):
    """"""
    print('load_publications..', end='')
    statement = r'INSERT INTO publications (title, "text", author, "category", created_at, changed_at) VALUES (%s,%s,%s,%s,%s,%s);'
    for row in gen_publications(conn, count=100):
        cursor.execute(statement, (row['title'],
                                   row['text'],
                                   row['author'],
                                   row['category'],
                                   row['created_at'],
                                   row['changed_at'],
                                   )
                       )
    print('OK')


def load_awards(conn, cursor):
    """"""
    print('load_awards..', end='')
    statement = r'INSERT INTO awards (film_award_id, movie_id, person_id, nomination_id) VALUES (%s,%s,%s,%s);'
    awards_list = list(gen_awards(conn))
    for row in awards_list:
        with conn:
            try:
                cursor.execute(statement, (row['film_award_id'],
                                           row['movie_id'],
                                           row['person_id'],
                                           row['nomination_id'],
                                           )
                               )
            except Exception:
                continue
    print('OK')


def load_cinema_movie_presence(conn, cursor):
    """"""
    print('load_cinema_movie_presence..', end='')
    statement = r'INSERT INTO cinema_online_movie_presence (movie_id, cinema_id, price, rating, discount, view_count, last_update' \
                r') VALUES (%s,%s,%s,%s,%s,%s,%s);'
    cinema_movie_presence_list = list(gen_cinema_movie_presence(conn))
    for row in cinema_movie_presence_list:
        with conn:
            try:
                cursor.execute(statement, (row['movie_id'],
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
    print('OK')


def load_user_movie_orders(conn, cursor):
    """"""
    print('load_user_movie_orders..', end='')
    statement = r'INSERT INTO user_movie_orders (cinema_order_id, movie_id, user_id, online_cinema_id, price, "date"' \
                r') VALUES (%s,%s,%s,%s,%s,%s);'
    for row in gen_user_movie_orders(conn):
        with conn:
            try:
                cursor.execute(statement, (row['cinema_order_id'],
                                           row['movie_id'],
                                           row['user_id'],
                                           row['online_cinema_id'],
                                           row['price'],
                                           row['date'],
                                           )
                               )
            except Exception:
                pass
    print('OK')


def load_users_rating(conn, cursor):
    """"""
    print('load_users_rating..', end='')
    statement = r'INSERT INTO users_rating (rating, user_id, movie_id, publication_id, created_at' \
                r') VALUES (%s,%s,%s,%s,%s);'
    for row in gen_users_rating(conn):
        cursor.execute(statement, (row['rating'],
                                   row['user_id'],
                                   row['movie_id'],
                                   row['publication_id'],
                                   row['created_at'],
                                   )
                       )
    print('OK')


def load_comments(conn, cursor):
    """"""
    print('load_comments..', end='')
    statement = r'INSERT INTO comments (user_id, "comment", parent_id, movie_id, publication_id, created_at, changed_at' \
                r') VALUES (%s,%s,%s,%s,%s,%s,%s);'
    for row in gen_comments(conn):
        cursor.execute(statement, (row['user_id'],
                                   row['comment'],
                                   row['parent_id'],
                                   row['movie_id'],
                                   row['publication_id'],
                                   row['created_at'],
                                   row['changed_at'],
                                   )
                       )
    print('OK')

if __name__ == '__main__':
    ''''''
    conn = psycopg2.connect(dsn='postgresql://postgres:POSTGRES6602!@10.66.2.134:5432/kinoteka?sslmode=require')
    # conn = psycopg2.connect(dsn='postgresql://postgres:POSTGRESQLHOME@nas:5432/kinoteka?sslmode=require')
    with conn.cursor() as cursor:
        # constant data
        load_tags(conn, cursor)
        load_publications_category(conn, cursor)
        load_award_registry(conn, cursor)
        load_awards_nominations(conn, cursor)
        load_persons_positions(conn, cursor)
        load_cinema_online(conn, cursor)
        load_movies_data(conn, cursor)
        load_users(conn, cursor)
        load_persons(conn, cursor)

        # related data
        load_movies_staff(conn, cursor)
        load_awards(conn, cursor)
        load_cinema_movie_presence(conn, cursor)
        load_user_movie_orders(conn, cursor)
        load_publications(conn, cursor)
        load_comments(conn, cursor)
        load_users_rating(conn, cursor)

        # fix transaction
        conn.commit()

import random

import psycopg2

from loads.dyn_loads import gen_awards, gen_cinema_movie_presence, gen_publications, gen_user_movie_orders, \
    gen_users_rating
from stat_loads import gen_tags_list, gen_persons_positions, gen_publications_category, \
    gen_awards_nominations, gen_awards_category, gen_person_data, gen_cinema_online, gen_movies_data, gen_users_data


# Заплнение статическими данными
def load_tags(conn, cursor):
    # tags
    statement = r"INSERT INTO tags (title) VALUES (%s);"
    for tag in gen_tags_list():
        print("INSERT: ", tag)
        cursor.execute(statement, (tag,))
    conn.commit()


def load_publications_category(conn, cursor):
    # tags
    statement = r"INSERT INTO publications_category (title) VALUES (%s);"
    for publications_category in gen_publications_category():
        print("INSERT: ", publications_category)
        cursor.execute(statement, (publications_category,))
    conn.commit()


def load_award_registry(conn, cursor):
    # tags
    statement = r"INSERT INTO film_award_registry (title) VALUES (%s);"
    for award in gen_awards_category():
        print("INSERT: ", award)
        cursor.execute(statement, (award,))
    conn.commit()


def load_awards_nominations(conn, cursor):
    # tags
    statement = r"INSERT INTO film_award_nominations_registry (title) VALUES (%s);"
    for nomination in gen_awards_nominations():
        print("INSERT: ", nomination)
        cursor.execute(statement, (nomination,))
    conn.commit()


def load_persons_positions(conn, cursor):
    # tags
    statement = r"INSERT INTO person_position (title) VALUES (%s);"
    for position in gen_persons_positions():
        print("INSERT: ", position)
        cursor.execute(statement, (position,))
    conn.commit()


def load_cinema_online(conn, cursor):
    # tags
    statement = r"INSERT INTO cinema_online (title, url) VALUES (%s,%s);"
    for row in gen_cinema_online():
        print("INSERT: ", row)
        cursor.execute(statement, (row['title'],
                                   row['url']
                                   ))
    conn.commit()


def load_persons(conn, cursor):
    # tags
    statement = r"INSERT INTO persons (country, name, birthday, bio) VALUES (%s,%s,%s,%s);"
    for row in gen_person_data():
        print("INSERT: ", row)
        cursor.execute(statement, (row['country'],
                                   row['name'],
                                   row['birthday'],
                                   row['bio'],
                                   )
                       )
    conn.commit()


def load_users(conn, cursor):
    # tags
    statement = r'INSERT INTO users (username, email, "password", fio, bio, created_at, birthday, last_logon) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);'
    for row in gen_users_data(count=100):
        try:
            print("INSERT: ", row)
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
    conn.commit()


def load_movies_data(conn, cursor):
    # tags
    statement = r'INSERT INTO movies (isbn, title, title_original, country, "year", budget, boxoffice, rating, duration, rars, tags, subject) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
    for row in gen_movies_data():
        print("INSERT: ", row)
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
    conn.commit()


def load_publications(conn, cursor):
    """"""
    statement = r'INSERT INTO publications (title, "text", author, "category", created_at, changed_at) VALUES (%s,%s,%s,%s,%s,%s);'
    for row in gen_publications(conn, count=100):
        print("INSERT: ", row)
        cursor.execute(statement, (row['title'],
                                   row['text'],
                                   row['author'],
                                   row['category'],
                                   row['created_at'],
                                   row['changed_at'],
                                   )
                       )
    conn.commit()


if __name__ == '__main__':
    ''''''
    # conn = psycopg2.connect(dsn='postgresql://dba:DBAHOME@nas:5432/kinoteka')
    # print(conn, conn.status)
    # with conn.cursor() as cursor:
        # constant data
        # load_tags(conn, cursor)
        # load_publications_category(conn, cursor)
        # load_award_registry(conn, cursor)
        # load_awards_nominations(conn, cursor)
        # load_persons_positions(conn, cursor)
        # load_cinema_online(conn, cursor)

        #
        # load_movies_data(conn, cursor)
        # load_users(conn, cursor)
        # load_persons(conn, cursor)
        # load_publications(conn, cursor)

        # for data in gen_users_rating(conn, count=10):
        #     print(data)

    print(random.choice(range(1000)))


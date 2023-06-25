import datetime
import json
import random
import uuid

from faker import Faker

en_fake = Faker()
ru_fake = Faker('ru_RU')

fakers = {
    'ru': Faker('ru_RU'),
    'en': Faker('en_US'),
    'es': Faker('es_ES'),
    'fr': Faker('fr_FR')
}
codes = list(fakers.keys())
domains_list = ('gmail.com', 'mail.ru', 'yandex.ru', 'vc.com', 'rambler.ru', 'cloud.com', 'yahoo.com', 'bk.ru')
tags_list = ('Боевик', 'Комедия', 'Триллер', 'Драма', 'Фантастика', 'Фентези', 'Ужасы',
             'Документальный', 'Эротика', 'Трэш', 'Мелодрама', 'Сериал', 'Шоу', 'Трагикомедия')
publications_category_list = ('Обзор', 'Эссе', 'Отзыв', 'Анонс', 'Рецензия', 'Статья', 'Аналитика')
person_positions_list = ('Режиссер', 'Актер', 'Продюсер', 'Оператор', 'Звуко-оператор', 'Постановщик',
                         'Художник по костюмам', 'Гример', 'Касадер', 'Специалист по спецэффектам',
                         'Ассистент режиссера', 'Ассистент оператора', 'Ассистент звуко-оператора', 'Свето-оператор',
                         'Разносчик кофе', 'Финансовый директор')
award_registry_list = ('Ника', 'Золотой глобус', 'Оскар', 'Каннские львы', 'Пальмовая ветвь', 'Сатурн', 'Золотой лев',
                       'Сезар', 'Золотая малина', 'Золотой орел', 'Asian Film Awards')

film_award_nominations_registry_list = ('Лучшая роль', 'Лучшая роль второго плана', 'Лучший звук',
                                        'Лучшие видео-эффекты',
                                        'Лучшая мужская роль', 'Лучшая мужская роль второго плана', 'Лучший дизайн',
                                        'Лучшая женская роль', 'Лучшая женская роль второго плана',
                                        'Лучшая хореография',
                                        'Лучшие видео-эффекты',
                                        'Лучший документальный фильм', 'Лучшая операторская работа',
                                        'Лучшая постановка',
                                        'Лучший сценарий', 'Лучший грим', 'Лучшие прически', 'Лучший мотаж',
                                        'Лучшая музыка',
                                        'Лучшие титры', 'Лучший кофе')

cinema_online_list = ('Кинопоиск', 'Окко', 'Иви', 'Премьер', 'Мегого', 'Kion', 'Netflix', 'Start',
                      'More.tv', 'Amediateka')


def gen_tags_list():
    for tag in tags_list:
        yield tag


def gen_publications_category():
    for publications_category in publications_category_list:
        yield publications_category


def gen_persons_positions():
    for position in person_positions_list:
        yield position


def gen_awards_category():
    for award in award_registry_list:
        yield award


def gen_awards_nominations():
    for nomination in film_award_nominations_registry_list:
        yield nomination


def gen_person_data(count=500000):
    for _ in range(count):
        i = random.choice(codes)
        fake = fakers[i]
        yield {
            'country': fake.current_country(),
            'name': fake.name(),
            'birthday': fake.date_of_birth(minimum_age=10, maximum_age=70),  # birthday
            'bio': ' '.join(ru_fake.sentences(nb=5)),
        }


def gen_movies_data(count=100000):
    ''''''
    for _ in range(count):
        i = random.choice(codes)
        fake = fakers[i]
        yield {
            'isbn': fake.sbn9(),
            'title': ru_fake.text(max_nb_chars=20),
            'title_original': fake.text(max_nb_chars=20),
            'country': fake.current_country(),
            'year': fake.year(),
            'budget': fake.numerify(text='%%%%%%%.%%'),
            'boxoffice': fake.numerify(text='%%%%%%%%.%%'),
            'rating': random.choice([1, 2, 3, 4, 5]),
            'duration': fake.time(end_datetime=datetime.timedelta(hours=1)),
            'rars': random.choice(['0+', '5+', '10+', '12+', '16+', '18+', '20+']),
            'tags': json.dumps(fake.random_choices(elements=tags_list, length=random.randint(1, 5))),
            'subject': ' '.join(ru_fake.texts(nb_texts=10)),
        }


def gen_cinema_online():
    for i in range(len(cinema_online_list)):
        yield {
            'title': cinema_online_list[i],
            'url': en_fake.uri(),
        }


def gen_users_data(count=5000000):
    for _ in range(count):
        yield {
            'username': ru_fake.user_name(),
            'email': ru_fake.email(domain=random.choice(domains_list)),
            'password': str(uuid.uuid4()),
            'fio': ru_fake.name(),
            'bio': ' '.join(ru_fake.sentences(nb=5)),
            'created_at': ru_fake.date_between(start_date='-10y'),
            'birthday': ru_fake.date_of_birth(minimum_age=17, maximum_age=60),  # birthday
            'last_logon': ru_fake.date_between(start_date='-1y'),
        }


if __name__ == '__main__':
    codes = list(fakers.keys())
    # for data in gen_person_data():
    #     print(data)

    for data in gen_cinema_online():
        print(data)

-- postgres sql

BEGIN;


CREATE TABLE tags
(
    title VARCHAR(56) NOT NULL UNIQUE
);
COMMENT ON TABLE tags IS 'Теги';


---


CREATE TABLE movies
(
    id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    isbn		   VARCHAR(12),
    title          VARCHAR NOT NULL,
    title_original VARCHAR,
    country        varchar(128),
    "year"         varchar(4),
    budget         NUMERIC(12,2) CHECK ( NULL OR budget >= 0 ),
    boxoffice      NUMERIC(12,2) CHECK ( NULL OR budget >= 0 ),
    rating         SMALLINT CHECK (rating > 0 AND rating < 6),
    duration       VARCHAR (8) NOT NULL,
    rars           VARCHAR(12),
    tags		   JSONB,
    subject		   TEXT
);
COMMENT ON TABLE movies IS 'Каталог кинолент и сериалов';


---


CREATE TABLE persons
(
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country    VARCHAR(128) NOT NULL,
    "name"     VARCHAR NOT NULL,
    birthday   DATE,
    bio        TEXT
);
COMMENT ON TABLE persons IS 'Актеры, режиссеры,...';


CREATE TABLE person_position
(
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(128) NOT NULL UNIQUE
);
COMMENT ON TABLE person_position IS 'Должности и выполняемые функции участников съемок';


CREATE TABLE movie_staff_m2m
(
    id           integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "character"  VARCHAR(128),          -- исполняемая роль
    is_lead_role BOOLEAN DEFAULT FALSE, -- главная роль
    position_id  SMALLINT NOT NULL REFERENCES person_position ON DELETE RESTRICT,
    person_id    INTEGER  NOT NULL REFERENCES persons ON DELETE RESTRICT,
    movie_id     INTEGER  NOT NULL REFERENCES movies ON DELETE CASCADE
);
COMMENT ON TABLE movie_staff_m2m IS 'Участники съемок';


---


CREATE TABLE film_award_registry
(
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title       VARCHAR(128) NOT NULL,
    description TEXT
);
COMMENT ON TABLE film_award_registry IS 'Существующие кино-премии мира';


CREATE TABLE film_award_nominations_registry
(
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title       VARCHAR NOT NULL,
    description TEXT
);
COMMENT ON TABLE film_award_registry IS 'Существующие номинации кино-премий';


CREATE TABLE awards
(
    id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    film_award_id  INTEGER  NOT NULL REFERENCES film_award_registry ON DELETE RESTRICT,
    movie_id       INTEGER  NOT NULL REFERENCES movies ON DELETE RESTRICT,
    person_id      INTEGER REFERENCES persons ON DELETE RESTRICT,
    nomination_id  INTEGER REFERENCES film_award_nominations_registry ON DELETE RESTRICT NOT NULL,
    CONSTRAINT award_nomination_unique_constraint UNIQUE (film_award_id, movie_id, nomination_id)
);
COMMENT ON TABLE awards IS 'Врученные награды кино-премий';


---


CREATE TABLE users
(
    id         integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username   VARCHAR(64)        NOT NULL UNIQUE,
    email      VARCHAR(128)       NOT NULL UNIQUE,
    "password" VARCHAR(128)       NOT NULL, -- password hash
    fio        VARCHAR(256)       NOT NULL,
    bio        TEXT,
    created_at DATE DEFAULT NOW() NOT NULL,
    deleted_at DATE,
    birthday   DATE               NOT NULL,
    last_logon DATE,
    CONSTRAINT user_birthday_check CHECK (birthday < NOW()),
    CONSTRAINT user_check_created_less_deleted CHECK (users.created_at <= users.deleted_at)
);
COMMENT ON TABLE users IS 'Пользователи кинотеки';


---


CREATE TABLE cinema_online
(
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(128) NOT NULL UNIQUE,
    url   TEXT         NOT NULL UNIQUE
);
COMMENT ON TABLE cinema_online IS 'Онлайн кинотеатры';


CREATE TABLE cinema_online_movie_presence
(
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    movie_id    INTEGER REFERENCES movies ON DELETE CASCADE,
    cinema_id   INTEGER REFERENCES cinema_online ON DELETE CASCADE,
    price       NUMERIC NOT NULL,
    rating      INTEGER NOT NULL,
    discount    SMALLINT DEFAULT 0 CHECK ( discount >= 0 OR discount <= 100 ), -- скидка для студентов
    view_count  INTEGER,
    last_update DATE,
    CONSTRAINT movie_cinema_rating_check CHECK (rating > 0 AND rating < 6),
    CONSTRAINT cinema_online_movie_presence_unique UNIQUE (movie_id, cinema_id)
);
COMMENT ON TABLE cinema_online_movie_presence IS 'Наличие фильмов в онлайн-кинотеатрах';


CREATE TABLE user_movie_orders
(
    id               integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cinema_order_id  uuid               NOT NULL,
    movie_id         INTEGER REFERENCES movies ON DELETE RESTRICT,
    user_id          INTEGER REFERENCES users ON DELETE RESTRICT,
    online_cinema_id INTEGER REFERENCES cinema_online ON DELETE RESTRICT,
    price            NUMERIC            NOT NULL CHECK ( price >= 0 ),
    "date"           DATE DEFAULT NOW() NOT NULL,
    CONSTRAINT user_movie_orders_m2m_pk2 UNIQUE (user_id, movie_id, online_cinema_id)
);
COMMENT ON TABLE user_movie_orders IS 'Заказы просмотров фильмов пользователями фильмов в онлайн-кинотеатрах';
COMMENT ON COLUMN user_movie_orders.cinema_order_id IS 'Идентификационный номер заказа в кинотеатре';


---


CREATE TABLE publications_category
(
    id    integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title VARCHAR(24) NOT NULL UNIQUE
);
COMMENT ON TABLE publications_category IS 'Категории публикаций (новости, обзор, анонс, ...)';



--- Публикации, обзоры, критика пользователей (студентов и преподавателей)
CREATE TABLE publications
(
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title       VARCHAR                                                     NOT NULL,
    "text"      TEXT                                                        NOT NULL,
    author      INTEGER REFERENCES users ON DELETE RESTRICT                 NOT NULL,
    "category"  INTEGER REFERENCES publications_category ON DELETE RESTRICT NOT NULL,
    created_at  DATE DEFAULT NOW()                                          NOT NULL,
    changed_at  DATE                                                        NOT NULL,
    tags		JSONB
);
COMMENT ON TABLE publications IS 'Публикации о кинематографе по категориям';


CREATE TABLE comments
(
    id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id        INTEGER            REFERENCES users ON DELETE SET NULL,
    "comment"      TEXT               NOT NULL,
    parent_id      INTEGER REFERENCES comments ON DELETE RESTRICT,
    movie_id       INTEGER REFERENCES movies ON DELETE CASCADE,
    publication_id INTEGER REFERENCES publications ON DELETE CASCADE,
    created_at     DATE DEFAULT NOW() NOT NULL,
    changed_at     DATE,
    CONSTRAINT comments_on_movie_and_publication_check -- комментарий только к фильму или публикации
        CHECK (NOT (movie_id IS NULL AND publication_id IS NULL) OR
               NOT (movie_id IS NOT NULL AND publication_id IS NOT NULL))
);
COMMENT ON TABLE comments IS 'Комментарии пользователей';


---
CREATE TABLE users_rating
(
    id             integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rating         SMALLINT  NOT NULL,
    user_id        INTEGER   NOT NULL REFERENCES users ON DELETE CASCADE,
    movie_id       INTEGER REFERENCES movies ON DELETE CASCADE,
    publication_id BIGINT REFERENCES publications ON DELETE CASCADE,
    created_at     TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT users_rating_unique_pk2 UNIQUE (movie_id, publication_id, user_id),
    CONSTRAINT user_rating_check_range_1_5 CHECK (rating > 0 AND rating < 6),
    CONSTRAINT user_comments_rating_check -- рейтинг только к фильму или публикации
        CHECK (NOT (movie_id IS NULL AND publication_id IS NULL) OR
               NOT (movie_id IS NOT NULL AND publication_id IS NOT NULL))
);
COMMENT ON TABLE users_rating IS 'Пользовательский рейтинг';

COMMIT;

-- INDEXES
-- CREATE INDEX movie_title_idx ON movies (title);
-- CREATE INDEX movie_title_original_idx ON movies (title_original);
-- CREATE INDEX movie_rating_idx ON movies (rating);
-- CREATE INDEX user_fio_idx ON users (fio);
-- CREATE INDEX person_name_idx ON persons ("name");
-- CREATE INDEX publications_title_idx ON publications (title);
-- CREATE INDEX publications_text_idx ON publications ("text");
-- CREATE INDEX publications_create_date_idx ON publications (created_at);


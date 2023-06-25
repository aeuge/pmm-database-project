# Проектирование и реализация сервиса "Онлайн-кинотека" с дополнительным мониторингом, используя инструмент PMM

## Схема бахзы даных сервиса "Онлайн-кинотека"

```sql
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
    duration       INTEGER	NOT NULL CHECK ( duration >= 0 ),
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
    last_name  VARCHAR(128) NOT NULL,
    first_name VARCHAR(128) NOT NULL,
    mid_name   VARCHAR(128),
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
    title       VARCHAR(128) NOT NULL,
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
    title       VARCHAR(256)                                                NOT NULL,
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


-- INDEXES
CREATE INDEX movie_title_idx ON movies (title);
CREATE INDEX movie_title_original_idx ON movies (title_original);
CREATE INDEX movie_rating_idx ON movies (rating);
CREATE INDEX user_fio_idx ON users (fio);
CREATE INDEX person_name_idx ON persons (last_name, first_name);
CREATE INDEX publications_title_idx ON publications (title);
CREATE INDEX publications_text_idx ON publications ("text");
CREATE INDEX publications_create_date_idx ON publications (created_at);

COMMIT;
```

## Установка клиента PMM и дополнений для postgresql на ноде с БД
Установку клиента PMM и расширений произведем на каждой ноде кластера
```bash
root@node0:~# wget https://repo.percona.com/apt/percona-release_latest.generic_all.deb
--2023-06-22 15:59:08--  https://repo.percona.com/apt/percona-release_latest.generic_all.deb
Resolving repo.percona.com (repo.percona.com)... 49.12.125.205, 142.132.159.91, 2a01:4f8:242:5792::2, ...
Connecting to repo.percona.com (repo.percona.com)|49.12.125.205|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 11804 (12K) [application/x-debian-package]
Saving to: ‘percona-release_latest.generic_all.deb’

percona-release_latest.generic_all.de 100%[======================================================================>]  11.53K  --.-KB/s    in 0s

2023-06-22 15:59:08 (251 MB/s) - ‘percona-release_latest.generic_all.deb’ saved [11804/11804]

root@node0:~# dpkg -i ./percona-release_latest.generic_all.deb

root@node0:~# apt-get update && apt install -y pmm2-client postgresql-contrib

...

root@node0:~# pmm-admin --version
ProjectName: pmm-admin
Version: 2.37.1
PMMVersion: 2.37.1
Timestamp: 2023-06-01 15:50:45 (UTC)
FullCommit: 03b95b3d05401a268eda3158db739f5f11a619de
```
Зарегистрируем агент мониторинга на сервере на каждой ноде кластера БД
```bash
root@node0:~# pmm-admin config --server-insecure-tls --server-url=https://admin:*****@10.128.0.17:443
Checking local pmm-agent status...
pmm-agent is running.
Registering pmm-agent on PMM Server...
Registered.
Configuration file /usr/local/percona/pmm2/config/pmm-agent.yaml updated.
Reloading pmm-agent configuration...
Configuration reloaded.
Checking local pmm-agent status...
pmm-agent is running.
```
Узнаем мастер-ноду и на мастер ноде patroni создадим пользователя для мониторинга
```bash
patronictl list
+--------+-------------+---------+---------+----+-----------+
| Member | Host        | Role    | State   | TL | Lag in MB |
+ Cluster: main (7244212832745550623) -----+----+-----------+
| node0  | 10.128.0.16 | Replica | running |  6 |         0 |
| node1  | 10.129.0.14 | Replica | running |  6 |         0 |
| node2  | 10.130.0.28 | Leader  | running |  6 |           |
+--------+-------------+---------+---------+----+-----------+
dba@node0:~$ patronictl switchover
Master [node2]:
Candidate ['node0', 'node1'] []: node0
When should the switchover take place (e.g. 2023-06-22T17:20 )  [now]:
Current cluster topology
+--------+-------------+---------+---------+----+-----------+
| Member | Host        | Role    | State   | TL | Lag in MB |
+ Cluster: main (7244212832745550623) -----+----+-----------+
| node0  | 10.128.0.16 | Replica | running |  6 |         0 |
| node1  | 10.129.0.14 | Replica | running |  6 |         0 |
| node2  | 10.130.0.28 | Leader  | running |  6 |           |
+--------+-------------+---------+---------+----+-----------+
Are you sure you want to switchover cluster main, demoting current master node2? [y/N]: y
2023-06-22 16:20:34.35033 Successfully switched over to "node0"
+--------+-------------+---------+---------+----+-----------+
| Member | Host        | Role    | State   | TL | Lag in MB |
+ Cluster: main (7244212832745550623) -----+----+-----------+
| node0  | 10.128.0.16 | Leader  | running |  6 |           |
| node1  | 10.129.0.14 | Replica | running |  6 |         0 |
| node2  | 10.130.0.28 | Replica | stopped |    |   unknown |
+--------+-------------+---------+---------+----+-----------+
dba@node0:~$ patronictl list
+--------+-------------+---------+---------+----+-----------+
| Member | Host        | Role    | State   | TL | Lag in MB |
+ Cluster: main (7244212832745550623) -----+----+-----------+
| node0  | 10.128.0.16 | Leader  | running |  7 |           |
| node1  | 10.129.0.14 | Replica | running |  6 |         0 |
| node2  | 10.130.0.28 | Replica | stopped |    |   unknown |
+--------+-------------+---------+---------+----+-----------+
dba@node0:~$ patronictl list
+--------+-------------+---------+---------+----+-----------+
| Member | Host        | Role    | State   | TL | Lag in MB |
+ Cluster: main (7244212832745550623) -----+----+-----------+
| node0  | 10.128.0.16 | Leader  | running |  7 |           |
| node1  | 10.129.0.14 | Replica | running |  7 |         0 |
| node2  | 10.130.0.28 | Replica | running |  7 |         0 |
+--------+-------------+---------+---------+----+-----------+


dba@node0:~$ sudo -u postgres psql
psql (14.8 (Ubuntu 14.8-0ubuntu0.22.04.1))
Type "help" for help.

postgres=# create user pmm with superuser encrypted password 'PMMPASS';
CREATE ROLE
postgres=# \du+
                                           List of roles
 Role name  |                         Attributes                         | Member of | Description
------------+------------------------------------------------------------+-----------+-------------
 dba        | Create role, Create DB                                     | {}        |
 pmm        | Superuser                                                  | {}        |
 postgres   | Superuser, Create role, Create DB, Replication, Bypass RLS | {}        |
 replicator | Replication                                                | {}        |
 rewind     |                                                            | {}        |

```

Добавляем в настройки patroni доступ пользователю pmm, настройки для мониторинга и перезагрузим кластер
```bash
dba@node0:~$ patronictl edit-config
---
+++
@@ -2,6 +2,8 @@
 loop_wait: 10
 maximum_lag_on_failover: 1048576
 postgresql:
   parameters:
     autovacuum_analyze_scale_factor: 0.01
+    shared_preload_libraries: 'pg_stat_statements'
+    track_activity_query_size: 2048
+    pg_stat_statements.track: all
+    track_io_timing: on

+  pg_hba:
+  - local  all    pmm       scram-sha-256

Apply these changes? [y/N]: y
Configuration changed
```
После внесения настроек кластеру требуется перезагрузка

```bash
dba@node0:~$ patronictl list
+--------+-------------+---------+---------+----+-----------+-----------------+
| Member | Host        | Role    | State   | TL | Lag in MB | Pending restart |
+ Cluster: main (7244212832745550623) -----+----+-----------+-----------------+
| node0  | 10.128.0.16 | Leader  | running |  7 |           | *               |
| node1  | 10.129.0.14 | Replica | running |  7 |         0 | *               |
| node2  | 10.130.0.28 | Replica | running |  7 |         0 | *               |
+--------+-------------+---------+---------+----+-----------+-----------------+
dba@node0:~$ patronictl restart main
+--------+-------------+---------+---------+----+-----------+-----------------+
| Member | Host        | Role    | State   | TL | Lag in MB | Pending restart |
+ Cluster: main (7244212832745550623) -----+----+-----------+-----------------+
| node0  | 10.128.0.16 | Leader  | running |  7 |           | *               |
| node1  | 10.129.0.14 | Replica | running |  7 |         0 | *               |
| node2  | 10.130.0.28 | Replica | running |  7 |         0 | *               |
+--------+-------------+---------+---------+----+-----------+-----------------+
When should the restart take place (e.g. 2023-06-22T18:02)  [now]:
Are you sure you want to restart members node2, node0, node1? [y/N]: y
Restart if the PostgreSQL version is less than provided (e.g. 9.5.2)  []:
Success: restart on member node2
Success: restart on member node0
Success: restart on member node1
dba@node0:~$ patronictl list
+--------+-------------+---------+---------+----+-----------+
| Member | Host        | Role    | State   | TL | Lag in MB |
+ Cluster: main (7244212832745550623) -----+----+-----------+
| node0  | 10.128.0.16 | Leader  | running |  8 |           |
| node1  | 10.129.0.14 | Replica | running |  8 |         0 |
| node2  | 10.130.0.28 | Replica | running |  8 |         0 |
+--------+-------------+---------+---------+----+-----------+
```
Проверим подключение к БД новым пользователем
```bash
dba@node0:~$ psql -U pmm -d postgres -h localhost
Password for user pmm:
psql (14.8 (Ubuntu 14.8-0ubuntu0.22.04.1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

postgres=# \c
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
You are now connected to database "postgres" as user "pmm".
postgres=#

```
Создадим расширение для мониторинга
```bash
dba@node0:~$ sudo -u postgres psql -c "CREATE EXTENSION pg_stat_statements SCHEMA public"
CREATE EXTENSION
```
### Подключение к мониторингу

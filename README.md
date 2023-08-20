# Проектирование и реализация сервиса "Онлайн-кинотека" с дополнительным мониторингом, используя инструмент PMM
## 1. подготовка схемы базы данных 
- [Схема базы даных сервиса "Онлайн-кинотека" (SQL: DDL)](loads/sql/create_tables.sql)
- [Схема базы даных сервиса "Онлайн-кинотека" (IMG: PNG)](assets/pics/kinoteka_db_schema.png)

## 2. Развертывание кластера БД
Кластер БД Postgresql [«Создание и тестирование высоконагруженного отказоустойчивого кластера PostgreSQL на базе Patroni»](https://github.com/aeuge/pmm-pg-patroni-cluster)

## 3. Развертывание схемы БД на кластере
На запущенном кластере БД создадим базу данных `kinoteka` и развернем схему БД:
```postgresql
postgres=# create database kinoteka owner dba;
CREATE DATABASE
postgres=# \c kinoteka dba
Password for user dba:
psql (15.3 (Debian 15.3-1.pgdg110+1), server 14.8 (Debian 14.8-1.pgdg110+1))
You are now connected to database "kinoteka" as user "dba".
kinoteka=> COMMENT ON database kinoteka is 'БД КИНОТЕКА - Каталог данных о фильмах и сериалах для студентов изучающих современное искусство';
COMMENT
kinoteka=>
\q
```
В терминале запусим SQL скрипт для создания таблиц и индексов. (В случае, если следующим шагом подразумевается 
заливка большого объема данных, создание индексов лучше произвести после заливки данных, для ускорения)
```shell
root@nas:/home/dba/sql# psql -U dba -h localhost -d kinoteka -f ./create_tables.sql
Password for user dba:
BEGIN
CREATE TABLE
COMMENT
CREATE TABLE
COMMENT
CREATE TABLE
COMMENT
CREATE TABLE
...
```
```postgresql
kinoteka=# \dt
                    List of relations
 Schema |              Name               | Type  | Owner
--------+---------------------------------+-------+-------
 public | awards                          | table | dba
 public | cinema_online                   | table | dba
 public | cinema_online_movie_presence    | table | dba
 public | comments                        | table | dba
 public | film_award_nominations_registry | table | dba
 public | film_award_registry             | table | dba
 public | movie_staff_m2m                 | table | dba
 public | movies                          | table | dba
 public | person_position                 | table | dba
 public | persons                         | table | dba
 public | publications                    | table | dba
 public | publications_category           | table | dba
 public | tags                            | table | dba
 public | user_movie_orders               | table | dba
 public | users                           | table | dba
 public | users_rating                    | table | dba
(16 rows)

kinoteka=# \di
                                        List of relations
 Schema |                 Name                 | Type  | Owner |              Table
--------+--------------------------------------+-------+-------+---------------------------------
 public | award_nomination_unique_constraint   | index | dba   | awards
 public | awards_pkey                          | index | dba   | awards
 public | cinema_online_movie_presence_pkey    | index | dba   | cinema_online_movie_presence
 public | cinema_online_movie_presence_unique  | index | dba   | cinema_online_movie_presence
 public | cinema_online_pkey                   | index | dba   | cinema_online
 public | cinema_online_title_key              | index | dba   | cinema_online
 public | cinema_online_url_key                | index | dba   | cinema_online
 public | comments_pkey                        | index | dba   | comments
 public | film_award_nominations_registry_pkey | index | dba   | film_award_nominations_registry
 public | film_award_registry_pkey             | index | dba   | film_award_registry
 public | movie_rating_idx                     | index | dba   | movies
 public | movie_staff_m2m_pkey                 | index | dba   | movie_staff_m2m
 public | movie_title_idx                      | index | dba   | movies
 public | movie_title_original_idx             | index | dba   | movies
 public | movies_pkey                          | index | dba   | movies
 public | person_name_idx                      | index | dba   | persons
 public | person_position_pkey                 | index | dba   | person_position
 public | person_position_title_key            | index | dba   | person_position
 public | persons_pkey                         | index | dba   | persons
 public | publications_category_pkey           | index | dba   | publications_category
 public | publications_category_title_key      | index | dba   | publications_category
 public | publications_create_date_idx         | index | dba   | publications
 public | publications_pkey                    | index | dba   | publications
 public | publications_text_gin_idx            | index | dba   | publications
 public | publications_title_idx               | index | dba   | publications
 public | tags_title_key                       | index | dba   | tags
 public | user_fio_idx                         | index | dba   | users
 public | user_movie_orders_m2m_pk2            | index | dba   | user_movie_orders
 public | user_movie_orders_pkey               | index | dba   | user_movie_orders
 public | user_username_idx                    | index | dba   | users
 public | users_email_key                      | index | dba   | users
 public | users_pkey                           | index | dba   | users
 public | users_rating_pkey                    | index | dba   | users_rating
 public | users_rating_unique_pk2              | index | dba   | users_rating
 public | users_username_key                   | index | dba   | users
(35 rows)

kinoteka=#
```
Для заполнения тестовыми данными создан [скрипт на Python](loads/main.py) с использованием библиотеки [Faker](https://pypi.org/project/Faker/)
```shell
$ python main.py 
load_tags..OK
load_publications_category..OK
load_award_registry..OK
load_awards_nominations..OK
load_persons_positions..OK
load_cinema_online..OK
load_movies_data..OK
load_users..OK
load_persons..OK
load_movies_staff..OK
load_awards..OK
load_cinema_movie_presence..OK
load_user_movie_orders..OK
load_publications..OK
load_comments..OK
load_users_rating..OK
```
```postgresql

kinoteka=# select * from users limit 3;

 id |    username     |         email          |               password               |              fio              |                                                                                                             bio                                                                                                             | created_at | deleted_at |  birthday  | last_logon
----+-----------------+------------------------+--------------------------------------+-------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+------------+------------+------------
  1 | sigizmund_2012  | kononovaverjan@mail.ru | d359956d-534e-4b45-8cd1-095c3cf02b1d | Меркушев Всемил Владиславович | Вперед приятель миф рота головной зеленый. Зачем сутки тесно нервно неожиданно. Затян
уться июнь смелый пробовать равнодушный возмутиться заплакать. Мера металл командир вряд человечек мимо. Блин приятель экзамен спасть. | 2021-08-11 |            | 1978-05-17 | 2023-03-22
  2 | nikolaevilarion | nikon2020@cloud.com    | ca6c7ebe-207d-4581-b058-91b2532f6f1f | Крылов Рубен Антипович        | Пропасть виднеться вообще коричневый природа легко бабочка. Легко носок успокоиться а
кадемик. Крыса белье цвет. Господь манера легко. Радость пол бок прощение вчера упорно устройство.                                     | 2022-03-16 |            | 1963-04-30 | 2022-11-13
  3 | luchezar1970    | maja_2002@mail.ru      | aba90c8f-5308-47bd-85c5-5a7e4bdc2249 | Рубен Феодосьевич Соловьев    | Багровый школьный нажать. Скользить наткнуться зеленый чувство. Строительство заработ
ать левый. Хотеть добиться затянуться предоставить. Виднеться сынок горький один каюта хозяйка уничтожение.                            | 2018-03-05 |            | 1997-11-16 | 2023-01-10
(3 rows)
```
В дальнейшем, для имитации работы пользователей с БД (через приложеие) запустим [скрипт](loads/async_load.py), 
который в асинхронном режиме будет добавлять, изменять и удалять записи в БД. 
```shell
$ python async_load.py 
Action: create user
Action: update publication (39)
Action: delete user (mark)
Action: create publication
Action: create comment publication (child=False)
Action: set user rating on publication
Action: set user rating on movie
Action: create comment movie (child=False)
Action: create user movie order
Action: create comment publication (child=False)
Action: create comment movie (child=False)
Action: set user rating on movie
Action: set user rating on publication
Action: create comment publication (child=True)
Action: create comment movie (child=True)
Action: create comment publication (child=False)
Action: create user movie order
Action: create comment publication (child=False)
Action: set user rating on publication
Action: set user rating on publication
Action: create comment movie (child=False)
Action: create comment publication (child=False)
Action: set user rating on movie
Action: create comment publication (child=True)
Action: set user rating on movie
...
```
## 4. Установка клиента PMM и дополнений для postgresql на ноде с БД
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
После настройки и запуска сервисов мониторинга, подключимся на web-интерфейс
![](assets/pics/logon.png)
Сменим пароль админа по-умолчанию и войдем в систему.
![](assets/pics/dashboard.png)
По-умолчанию откроется `dashboard`. Выберем мониторинг добавленных серверов БД
![](assets/pics/pg_instance_overview.png)
Просмотрим общую статистику
![](assets/pics/pg_instance_summary.png)
Или статистику по конкретным нодам
![](assets/pics/pg_instance_node2_down.png)
Мониторинг `node2` показывает, что сней не все в порядке - выясняется, что у ноды проблемы с репликацией.

---

Теория рассказывает, а практика подтверждает, что в современных условиях и сложных технологиях мониторинг необходим 
как воздух для контроля и быстрого выявления проблем.

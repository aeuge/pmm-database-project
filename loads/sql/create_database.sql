CREATE DATABASE kinoteka owner dba;
\connect kinoteka
CREATE SCHEMA kinoteka AUTHORIZATION dba;
ALTER DATABASE kinoteka SET search_path = kinoteka,public;
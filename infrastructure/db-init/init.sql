CREATE USER nidus_app_user WITH PASSWORD 'nidus_app_secret';

CREATE DATABASE nidus_test;

\c nidus_core;
GRANT ALL PRIVILEGES ON SCHEMA public TO nidus_app_user;

\c nidus_test;
GRANT ALL PRIVILEGES ON SCHEMA public TO nidus_app_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO nidus_admin;
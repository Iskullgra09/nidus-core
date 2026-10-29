#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Restricted application user (RLS enforced at runtime)
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$APP_USER') THEN
            CREATE USER $APP_USER WITH PASSWORD '$APP_PASSWORD';
        END IF;
    END
    \$\$;

    -- Isolated test database (pytest never touches POSTGRES_DB)
    SELECT 'CREATE DATABASE $POSTGRES_TEST_DB'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_TEST_DB')\gexec

    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $APP_USER;
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_TEST_DB TO $POSTGRES_USER;
    GRANT CONNECT ON DATABASE $POSTGRES_TEST_DB TO $APP_USER;
EOSQL

# Schema grants on the test DB (tables appear after alembic migrate_test_db.py)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_TEST_DB" <<-EOSQL
    GRANT USAGE ON SCHEMA public TO $APP_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $APP_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO $APP_USER;
EOSQL

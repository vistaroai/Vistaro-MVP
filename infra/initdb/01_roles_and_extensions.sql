-- DB-001 bootstrap: roles and extensions for the Vistaro database.
-- Runs automatically on a fresh Postgres volume (mounted by
-- infra/docker-compose.yml) and is idempotent, so it can also be run manually
-- against an existing volume. These are local development passwords only;
-- staging sets real passwords from the platform secret store.

CREATE EXTENSION IF NOT EXISTS citext;

DO $bootstrap$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'vistaro_migrator') THEN
        -- Owns and evolves the schema; never connects to serve requests.
        CREATE ROLE vistaro_migrator LOGIN PASSWORD 'vistaro_migrator_local_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'vistaro_app') THEN
        -- Serves requests; cannot bypass Row Level Security.
        CREATE ROLE vistaro_app LOGIN PASSWORD 'vistaro_app_local_only'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
    END IF;
END
$bootstrap$;

-- PostgreSQL 15+ no longer grants CREATE on the public schema to PUBLIC.
GRANT CONNECT ON DATABASE vistaro TO vistaro_migrator, vistaro_app;
GRANT USAGE, CREATE ON SCHEMA public TO vistaro_migrator;
GRANT USAGE ON SCHEMA public TO vistaro_app;

# Deploying Concretethings to Supabase (Postgres) and migrating data

This guide shows a safe path to migrate the local SQLite database to Supabase Postgres and deploy the application.

Prerequisites
- A Supabase account and a project
- The project `DATABASE_URL` (connection string) and service key
- `psql` or Supabase SQL Editor access to the project
- Docker (recommended) or Python 3.11+ environment

High-level steps
1. Create a Supabase project.
2. Create a new Database user and note the connection string (DATABASE_URL). You can use the primary connection string for initial migrations, but rotate credentials afterwards.
3. Configure storage for uploads (Supabase Storage) and note the bucket details.
4. In the repository, set `DATABASE_URL` to the Supabase Postgres connection string.
5. Run the migration script to copy data from `data.sqlite3` into Supabase:

```bash
export DATABASE_URL="postgresql://user:pass@dbhost:5432/dbname"
python3 scripts/migrate_sqlite_to_postgres.py
```

6. Verify data in the Supabase SQL editor and check row counts for critical tables.
7. Configure environment variables for the app (JWT secret, mail settings, Twilio, Supabase storage keys) and run the app in Docker or directly with Gunicorn.

Quick Docker deployment (example)

1. Build the container:

```bash
docker build -t concretethings:latest .
```

2. Run with the DATABASE_URL and other secrets:

```bash
docker run -e DATABASE_URL="$DATABASE_URL" -e JWT_SECRET_KEY="SOMETHING" -p 8001:8001 concretethings:latest
```

Notes and caveats
- Test the migration on a staging Supabase project first.
- The migration script attempts to preserve numeric primary keys and set Postgres sequences. If your models use composite keys or custom PKs, inspect results manually.
- Move file storage to Supabase Storage in production. The app currently uses `uploads/` local folder; hook uploads endpoints to use Supabase Storage SDK or S3-compatible API.
- Rotate any service keys used in the migration and avoid storing secrets in the repository.

If you want, I can:
- Run the migration locally (if you provide a temporary Supabase DATABASE_URL).
- Add a production-ready Docker Compose file or Kubernetes manifests.
- Integrate Supabase Storage in the upload endpoints.

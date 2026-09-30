# Migrations

For v0.0 the FastAPI lifespan creates tables for local development. Before a shared or production deployment, initialize Alembic against `backend/app/models.py` and apply revisions through the deployment pipeline. This avoids database schema changes being coupled to application startup.

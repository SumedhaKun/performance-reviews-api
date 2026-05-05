import os

import sqlalchemy


def get_database_url():
    database_url = os.getenv(
        "POSTGRES_URI",
        "postgresql+psycopg://myuser:mypassword@localhost/pr_database",
    )

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    return database_url


engine = sqlalchemy.create_engine(get_database_url())

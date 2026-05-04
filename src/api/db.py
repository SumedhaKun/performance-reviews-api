import os

import psycopg
from psycopg.rows import dict_row


def get_connection():
    database_url = os.getenv(
        "POSTGRES_URI",
        "postgresql://myuser:mypassword@localhost/pr_database",
    )

    return psycopg.connect(database_url, row_factory=dict_row)

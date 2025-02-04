# db.py
# Ojos Project
# 
# Not a blueprint. Rather, a set of functions to help with database management.
import psycopg2
import os
from .app import DB

def _create_tables():
    schema_path = os.path.join(os.getcwd(), "schema.sql")
    schema_sql = ""
    with open(schema_path, "r+") as f:
        schema_sql = f.read()

    with psycopg2.connect(DB) as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)

#!/usr/bin/env python
"""
Database reset script - drops all tables and recreates them fresh with CASCADE.
Run this to sync the database schema with the models.
"""


# also this will be removed and this file was utilized due to alembic not being initialized and migrations were not created so

import sys
sys.path.insert(0, '/c/Users/anujb/Documents/code/python-grpc-learning/client')

from sqlalchemy import text
from db import engine, Base

if __name__ == "__main__":
    print("Dropping existing database tables with CASCADE...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS todo CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
    print("✓ Tables dropped")
    
    print("Creating new database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    print("\n✅ Database reset complete!")



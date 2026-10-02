from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


"""
# create a new database and user for the application

        sudo mariadb or sudo mysql

        CREATE DATABASE dentist_ai;

        CREATE USER 'dentist_ai'@'localhost'
        IDENTIFIED BY 'your_strong_password';

        GRANT ALL PRIVILEGES ON dentist_ai.* 
        TO 'dentist_ai'@'localhost';

        FLUSH PRIVILEGES;

        EXIT;
"""
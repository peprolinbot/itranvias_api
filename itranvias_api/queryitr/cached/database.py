from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import os
from .models import Base


class Database:
    def __init__(self, db_path: str):
        """
        Initialize the Database class with the path to the SQLite database.

        :param db_path: Path to the SQLite database file.
        """

        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def initialize_database(self):
        """
        Create all tables in the database if they don't exist.
        """

        Base.metadata.create_all(self.engine)

    def get_session(self):
        """
        Get a new session for database operations.

        :return: A new SQLAlchemy session.
        """

        return self.Session()

    def close_session(self):
        """
        Close the current session.
        """

        self.Session.remove()

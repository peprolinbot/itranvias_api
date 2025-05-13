from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from appdirs import user_data_dir

Base = declarative_base()


class Database:
    def __init__(self, db_path: str, language="en", updater=None):
        """
        Initialize the Database class with the path to the SQLite database.

        :param db_path: Path to the SQLite database file.
        :param language: The language to pass to the updater
        :param updater: A callable wich will receive a `session` and `language` parameters. Its output will be forwaded when calling `self.update()`.
        """

        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.Session = scoped_session(sessionmaker(bind=self.engine))

        self.language=language
        self.updater=updater
        

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

    def update(self):
        return self.updater(session=self.get_session(),language=self.language)


default_db = Database(f"{user_data_dir("itranvias_api","peprolinbot")}.sqlite3")
default_db.initialize_database()
default_session = default_db.get_session()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session,Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from appdirs import user_data_dir

Base = declarative_base()
"""@private"""

class Database:
    """
    An SQLAlchemy-powered database for itranvias_api "static" data
    """

    def __init__(self, db_path: str, language="en", updater=None):
        """
        :param db_path: Path to the SQLite database file.
        :param language: The language to pass to the updater
        :param updater: A callable wich will receive session=`get_session()` and language=`language` as parameters. Its output will be forwaded when calling `update()`.
        """

        self.db_path = db_path
        """Path to the SQLite database file."""
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        """This database's SQLAlchemy engine"""
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        """A scoped session manager"""

        self.language = language
        """
        The language for the data in the database
        """

        self.updater = updater
        """
        The updater function
        """

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

    def update(self, **kwargs):
        """
        Call the updater with a new session, this database's language, and forward other keyword arguments
        """

        return self.updater(
            session=self.get_session(), language=self.language, **kwargs
        )


default_db: Database = Database(f"{user_data_dir("itranvias_api","peprolinbot")}.sqlite3")
"""
The default database for the library, stored in `~/.local/share/itranvias_api.sqlite3` or equivalents (powered by [appdirs](https://pypi.org/project/appdirs/))
"""
default_db.initialize_database()
default_session: Session = default_db.get_session()
"""
A default session for the default database
"""

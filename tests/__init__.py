import os

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session

from database.db_tables import Meetings


def setup_module():
    global transaction, connection, engine

    # Connect to the database and create the schema within a transaction
    engine = create_engine('sqlite:///test_db')
    connection = engine.connect()
    transaction = connection.begin()
    Meetings.metadata.create_all(connection)


def teardown_module():
    # Roll back the top level transaction and disconnect from the database
    transaction.rollback()
    connection.close()
    engine.dispose()

    # Delete database file
    os.remove('test_db.db')


class DatabaseTest(object):
    def setup(self):
        self.__transaction = connection.begin_nested()
        self.session = Session(connection)

    def teardown(self):
        self.session.close()
        self.__transaction.rollback()

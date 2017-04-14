# Standard imports
import os

# Third party imports
import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker

# Local imports
from database import db_tables as tables


# These database functions can be called from a number of
# different repos. Without specifying an absolute path, a
# new database file would be created in the root directories
# of each repo that uses a Session() object.
# This method strips the filepath down to `functions` and
# then points it to create a meetings.db file within `database`.
package_path = os.path.abspath(os.path.dirname(__file__))


# SQLite is used to maintain a local database
db_path = os.path.join(package_path,'meetings.db')
dialect = 'sqlite:///'

# Combine the dialect and path names to use as params for the engine
engine_params = dialect + db_path

engine = sql.create_engine(engine_params, echo=False)
tables.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


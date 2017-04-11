# Local imports
import database.db_tables as tables
import database.db_logging as db
from database import Session

session = Session()

mainentry = session.query(tables.Meetings).all()

# Third party imports

# Local imports
import database.db_tables as tables
import database.db_logging as db

from database import Session

session = Session()

mainentry = session.query(tables.MainPaperInfo).all()
refs = session.query(tables.References).all()
mapping = session.query(tables.RefMapping).all()


import pdb
pdb.set_trace()

from meeting import Meeting
from sqlalchemy.exc import IntegrityError

from functions.database import (
    db_errors, db_interface, db_logging,
    db_tables
)

from tests import DatabaseTest

new_meeting = {
    'day': 'Mon 3/14',
    'room_number': 1,
    'room_name': 'Glacier',
    'start_time': '9:00',
    'end_time': None,

    'mentor': 'Thom Yorke',
    'company': 'Radiohead',
    'associate': 'Keaton',
}

newer_meeting = {
    'day': 'Mon 3/14',
    'room_number': 1,
    'room_name': 'Glacier',
    'start_time': '9:00',
    'end_time': None,

    'mentor': 'Jonny Greenwood',
    'company': 'Halp',
    'associate': 'No',
}

new_m = Meeting(new_meeting)


class TestDatabase(DatabaseTest):
    pass

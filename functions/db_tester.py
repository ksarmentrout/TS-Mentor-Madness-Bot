from meeting import Meeting
from sqlalchemy.exc import IntegrityError
import database.db_interface as db

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

# try:
#     db.add_to_db(new_m)
# except IntegrityError:
#     pass

# print(db.get_all_meetings())

# print(db.meeting_search({'company': 'Radiohead'}))

# db.update_saved_meeting(Meeting(new_meeting), Meeting(newer_meeting))
# print('\n\nUpdated\n\n')

# print(db.get_all_meetings())

# print(db.meeting_search({'day': 'Mon 2/13', 'room_number': 6}))
#
# print(len(db.get_all_meetings()))


df = db.get_db_as_df()


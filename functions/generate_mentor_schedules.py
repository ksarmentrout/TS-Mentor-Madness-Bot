import email_sender
from database import db_interface as db
from functions.utilities import utils
from functions.utilities import variables as vrs


def main(specific_day=None):
    # Set variables
    sheet_options = vrs.sheet_options

    # Determine which day to send for
    match_day = utils.get_next_day()

    if specific_day:
        match_day = specific_day

    # Pick out the appropriate sheet names from the list
    sheet_names = [x for x in sheet_options if match_day in x]

    mentor_dict = {}

    for day in sheet_names:
        # Get all meetings in a given day
        all_meetings = db.meeting_search({'day': day})

        # Create a field for each new mentor if it doesn't already exist.
        # If it does, append the meeting
        for meeting in all_meetings:
            if meeting.mentor not in mentor_dict:
                mentor_dict[meeting.mentor] = [meeting]
            else:
                mentor_dict[meeting.mentor].append([meeting])

    email_sender.make_daily_mentor_schedules(mentor_dict)
    email_sender.make_mentor_packet_schedules(mentor_dict)


if __name__ == '__main__':
    main()

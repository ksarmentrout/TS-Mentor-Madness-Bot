from collections import defaultdict

import email_sender
from database import db_interface as db
from functions.utilities import utils
from functions.utilities import variables as vrs


def main(specific_day=None):
    """
    Mentors are given personalized schedules as they walk in each day
    for their meetings. This function gets each mentor scheduled for a
    given day (or the day after it is called, if no specific day is
    specified), and makes formatted schedule pages based on lists
    of their meetings.

    This function also generates and saves the bodies of reminder emails
    that can be sent out before the meetings.

    :param specific_day: str of day for which to create mentor schedules
    """
    # Set variables
    sheet_options = vrs.sheet_options

    # Determine which day to send for
    match_day = utils.get_next_day()

    if specific_day:
        match_day = specific_day

    # Pick out the appropriate sheet names from the list
    sheet_names = [x for x in sheet_options if match_day in x]

    mentor_dict = defaultdict(list)

    for day in sheet_names:
        # Get all meetings in a given day
        all_meetings = db.meeting_search({'day': day})

        # Append the meeting to the appropriate mentor's list
        for meeting in all_meetings:
            mentor_dict[meeting.mentor].append(meeting)

    # Generate email bodies
    email_sender.make_daily_mentor_schedules(mentor_dict)

    # Generate the formatted, printable schedules
    email_sender.make_mentor_packet_schedules(mentor_dict)


if __name__ == '__main__':
    main()

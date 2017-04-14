import csv
from datetime import datetime

import email_sender
import gcal_scheduler
from meeting import Meeting
from functions.utilities import utils
from functions.utilities import variables as vrs
from database import db_interface as db


def main():
    # Make Google API object
    sheets_api = utils.google_sheets_login()

    # Set variables
    spreadsheet_id = vrs.spreadsheet_id
    room_mapping = vrs.room_mapping
    sheet_options = vrs.sheet_options
    full_range = vrs.full_range
    lookahead = vrs.lookahead_days

    # Determine which days to check for.
    # Find index of today's date
    today_date = utils.get_today(skip_weekends=True)
    day_index = -1
    for idx, date in enumerate(sheet_options):
        if today_date in date:
            day_index = idx
            break

    if day_index == -1:
        raise IndexError("Today's date not found within sheet_options."
                         "If Mentor Madness has ended, please shut off this"
                         "update script.")

    # Set the days to check, without worrying about going past the program end
    sheet_names = [sheet_options[day_index]]
    idx = 1
    while lookahead > 0:
        try:
            sheet_names.append(sheet_options[day_index + idx])
            idx += 1
            lookahead -= 1
        except IndexError:
            break

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range

        # Get the sheet
        new_sheet = utils.get_sheet(sheets_api, spreadsheet_id=spreadsheet_id, sheet_query=sheet_query)

        # Load new sheet
        reader = csv.reader(new_sheet)

        # Create holder for current state of meetings
        current_meeting_list = []

        for row in reader:
            timeslot = parse_timeslot(row[0])

            # Make each rows the full length if it is not
            if len(row) < vrs.row_length:
                row.extend([''] * (vrs.row_length - len(row)))

            # Iterate over rooms
            for room_num in range(1, len(room_mapping) + 1):
                # Get descriptive variables of room
                room_dict = room_mapping[room_num]

                meeting_info = {
                    'start_time': timeslot,
                    'room_name': room_dict['name'],
                    'mentor': row[room_dict['mentor_col']],
                    'company': row[room_dict['company_col']],
                    'associate': row[room_dict['associate_col']],
                    'day': day
                }

                current_meeting = Meeting(meeting_info)

                current_meeting_list.append(current_meeting)

        # Compare the current version of the meeting with old meetings
        update_dict = db.process_changes(current_meeting_list)

        # Get the adding and deleting dictionaries
        adding = update_dict['adding']
        deleting = update_dict['deleting']

        # Send emails
        email_sender.send_update_mail(adding, deleting)
        gcal_scheduler.update_cal_events(adding, deleting)


def parse_timeslot(timeslot):
    return timeslot


if __name__ == '__main__':
    main()
    print('Ran successfully')

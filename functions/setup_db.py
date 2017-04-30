from meeting import Meeting
from functions.utilities import utils
from functions.utilities import variables as vrs
from database import db_interface as db


def main(delete_all_prev_meetings=False):
    # Make Google API object
    sheets_api = utils.google_sheets_login()

    # Set variables
    spreadsheet_id = vrs.spreadsheet_id
    room_mapping = vrs.room_mapping
    sheet_names = vrs.sheet_options
    full_range = vrs.full_range

    # Create holder for current state of meetings
    current_meeting_list = []

    if delete_all_prev_meetings:
        prev_meetings = db.get_all_meetings()
        db.delete_meeting(prev_meetings)
        print('Deleted previous meetings in database')

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range

        # Get the sheet
        new_sheet = utils.get_sheet(sheets_api, spreadsheet_id=spreadsheet_id, sheet_query=sheet_query)

        for row in new_sheet:
            timeslot = utils.parse_timeslot(row[0])
            if timeslot:
                timeslot = timeslot.strip()

            # This skips the first row, which doesn't have a timeslot (heading row)
            if not timeslot:
                continue

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
                    'room_number': room_num,
                    'mentor': row[room_dict['mentor_col']].strip(),
                    'company': row[room_dict['company_col']].strip(),
                    'associate': row[room_dict['associate_col']].strip(),
                    'day': day
                }

                current_meeting = Meeting(meeting_info)

                # Only add the meeting if there is a mentor,
                # company, or associate in it.
                if not current_meeting.is_populated:
                    continue

                current_meeting_list.append(current_meeting)

    # Add all meetings
    db.add_to_db(current_meeting_list)


if __name__ == '__main__':
    main(delete_all_prev_meetings=True)
    print('Ran successfully')

import email_sender
from functions.utilities import utils
from functions.utilities import variables as vrs


def main(specific_day=None):
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    # Set variables
    spreadsheet_id = vrs.spreadsheet_id
    room_mapping = vrs.room_mapping
    full_range = vrs.full_range
    sheet_options = vrs.sheet_options

    # Determine which day to send for
    match_day = utils.get_next_day()

    if specific_day:
        match_day = specific_day

    # Pick out the appropriate sheet names from the list
    sheet_names = [x for x in sheet_options if match_day in x]

    mentor_dict = {}

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range

        # Get the sheet
        new_sheet = utils.get_sheet(sheets_api, spreadsheet_id=spreadsheet_id, sheet_query=sheet_query)

        for row in new_sheet:
            timeslot = row[0]

            # Iterate over rooms
            for room_num in range(1, 7):
                # Get descriptive variables of room
                room_dict = room_mapping[room_num]
                room_name = room_dict['name']
                mentor_name = row[room_dict['mentor_col']]

                if not mentor_name:
                    continue

                # Add mentor to mentor list for the day
                if mentor_dict.get(mentor_name) is None:
                    mentor_dict[mentor_name] = []

                teamname_idx = room_dict['check_range'][0]
                teamname = utils.process_name(row[teamname_idx])
                if teamname:
                    new_event_dict = {'time': timeslot, 'mentor': mentor_name, 'company': teamname,
                                      'room_num': str(room_num), 'room_name': room_name, 'day': day}
                    mentor_dict[mentor_name].append(new_event_dict)

    email_sender.make_daily_mentor_schedules(mentor_dict)
    email_sender.make_mentor_packet_schedules(mentor_dict)


if __name__ == '__main__':
    main()

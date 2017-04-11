import time

import email_sender
from functions.utilities import utils
from functions.utilities import directories as dr
from functions.utilities import variables as vrs


def main():
    # Make Google API object
    sheets_api = utils.google_sheets_login()

    # Set variables
    spreadsheet_id = vrs.spreadsheet_id
    room_mapping = vrs.room_mapping
    full_range = vrs.full_range
    name_dict = dr.empty_name_dict

    # Determine which days to check for
    today = time.localtime()
    day = today.tm_mday

    if day > 24:
        sheet_names = vrs.week3
    elif day > 17:
        sheet_names = vrs.week2
    else:
        sheet_names = vrs.week1

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range

        # Get the sheet
        new_sheet = utils.get_sheet(sheets_api, spreadsheet_id=spreadsheet_id, sheet_query=sheet_query)

        # Add a spacer dict to separate days
        spacer_dict = {'time': None, 'mentor': None,
                       'room_num': None, 'room_name': None, 'day': day}
        for key, val in name_dict.items():
            name_dict[key].append(spacer_dict)

        for row in new_sheet:
            timeslot = row[0]

            # Iterate over rooms
            for room_num in range(1, len(room_mapping.keys()) + 1):
                # Get descriptive variables of room
                room_dict = room_mapping[room_num]
                room_name = room_dict['name']
                mentor_name = row[room_dict['mentor_col']]

                for col_num in room_dict['check_range']:
                    name = utils.process_name(row[col_num])
                    if name and name != 'not_found':
                        new_event_dict = {'time': timeslot, 'mentor': mentor_name,
                                          'room_num': str(room_num), 'room_name': room_name, 'day': day}
                        name_dict[name].append(new_event_dict)

    email_sender.send_weekly_mail(name_dict)


if __name__ == '__main__':
    main()

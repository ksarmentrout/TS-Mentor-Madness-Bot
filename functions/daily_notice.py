import traceback

import email_sender
import gcal_scheduler
from meeting import Meeting
from functions.utilities import utils as utils
from functions.utilities import variables as vrs
from functions.utilities import directories as dr


def main(team=None, specific_day=None, send_emails=True, create_calendar_events=False):
    # Make Google API object
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

    if team is None:
        name_dict = dr.empty_name_dict
    else:
        name_dict = {}
        if isinstance(team, list):
            for t in team:
                name_dict[t] = []
        else:
            name_dict[team] = []

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range

        # Get the sheet
        new_sheet = utils.get_sheet(sheets_api, spreadsheet_id=spreadsheet_id, sheet_query=sheet_query)

        # Add a spacer dict to separate days
        spacer_dict = {'time': None, 'mentor': None,
                       'room_num': None, 'room_name': None, 'day': day}
        spacer_mtg = Meeting(spacer_dict)

        for key, val in name_dict.items():
            name_dict[key].append(spacer_mtg)

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
                    if name and name != 'not_found' and name in name_dict.keys():
                        new_event_dict = {'time': timeslot, 'mentor': mentor_name, 'name': name,
                                          'room_num': str(room_num), 'room_name': room_name, 'day': day}
                        name_dict[name].append(new_event_dict)

        print('Got info for ' + day)

    try:
        if create_calendar_events:
            for name, event_list in name_dict.items():
                # event_list['name'] = name
                gcal_scheduler.add_cal_events(event_list)
    except Exception:
        traceback.print_exc()

    if send_emails:
        try:
            email_sender.send_daily_mail(name_dict)
        except Exception:
            traceback.print_exc()
        return None
    else:
        return name_dict


if __name__ == '__main__':
    main(create_calendar_events=False, send_emails=True, specific_day='Mon 3/6')
    # main()

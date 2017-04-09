import os
import time
import traceback

import gcal_scheduler
import directories as dr
import variables as vrs
import email_sender
import utils


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
        csv_name = utils.day_to_filename(day)

        # Make request for sheet
        sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_query).execute()
        new_sheet = sheet['values']
        new_sheet = new_sheet[1:]  # Get rid of the header row
        for idx, new_sheet_row in enumerate(new_sheet):
            if len(new_sheet_row) < vrs.row_length:
                new_sheet[idx].extend([''] * (vrs.row_length - len(new_sheet_row)))

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

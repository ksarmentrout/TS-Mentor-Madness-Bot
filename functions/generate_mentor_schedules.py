import os

import directories as dr
from apiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

from scheduling_bot.email_sender import *


def main():
    # Get credentials from Google Developer Console
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    secret_key_json = dr.LOCAL_PATH + 'MM Bot-32fa78cfd51b.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(secret_key_json, scopes=scopes)

    # Authenticate using Http object
    http_auth = credentials.authorize(Http())

    # Build Google API response object for sheets
    sheets_api = build('sheets', 'v4', credentials=credentials)

    # Set spreadsheet ID
    spreadsheet_id = '18gb1ehs9-hmXbIkKaTcLUvurzAJzpjDiXgNFZeazrNA'  # This is the MM spreadsheet
    # spreadsheet_id = '1qdAgkuyAl6DRV3LRn-zheWSiD-r4JIya8Ssr6-DswY4'  # This is my test spreadsheet

    # Set room mapping
    room_mapping = dr.room_mapping

    # Set query options
    sheet_options = [
        'Mon 2/13', 'Tues 2/14', 'Wed 2/15', 'Thurs 2/16', 'Fri 2/17',
        'Mon 2/20', 'Tues 2/21', 'Wed 2/22', 'Thurs 2/23', 'Fri 2/24',
        'Mon 2/27', 'Tues 2/28', 'Wed 3/1', 'Thurs 3/2', 'Fri 3/3',
        'Mon 3/6', 'Tues 3/7', 'Wed 3/8'
        ]

    sheet_names = ['Wed 3/8']

    full_range = dr.full_range

    mentor_dict = {}

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range
        csv_name = day_to_filename(day)

        # Make request for sheet
        sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_query).execute()
        new_sheet = sheet['values']
        new_sheet = new_sheet[1:]  # Get rid of the header row

        # Make sure each row is the correct length
        for idx, new_sheet_row in enumerate(new_sheet):
            if len(new_sheet_row) < 19:
                new_sheet[idx].extend([''] * (19 - len(new_sheet_row)))

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
                teamname = process_name(row[teamname_idx])
                if teamname:
                    new_event_dict = {'time': timeslot, 'mentor': mentor_name, 'company': teamname,
                                      'room_num': str(room_num), 'room_name': room_name, 'day': day}
                    mentor_dict[mentor_name].append(new_event_dict)

    make_daily_mentor_schedules(mentor_dict)
    make_mentor_packet_schedules(mentor_dict)


def day_to_filename(day):
    csv_name = day.replace(' ', '_').replace('/', '_') + '.csv'
    csv_name = '/cached_schedules/' + csv_name
    dirname = os.path.dirname(__file__)
    csv_name = dirname + csv_name
    return csv_name


if __name__ == '__main__':
    main()

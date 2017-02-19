import time
import csv
import os

from httplib2 import Http

from apiclient.discovery import build
# from oauth2client.client import GoogleCredentials
# from oauth2client.contrib.appengine import AppAssertionCredentials
from oauth2client.service_account import ServiceAccountCredentials

from . import directories as dr
from . import email_sender
from .utils import google_sheets_login

LOCAL_PATH = "/Users/keatonarmentrout/Desktop/Techstars/Mentor Madness/"


def main(team=None, specific_day=None, send_emails=True):
    # Build Google API response object for sheets
    sheets_api = google_sheets_login()

    # Set spreadsheet ID
    spreadsheet_id = '18gb1ehs9-hmXbIkKaTcLUvurzAJzpjDiXgNFZeazrNA'  # This is the MM spreadsheet
    # spreadsheet_id = '1qdAgkuyAl6DRV3LRn-zheWSiD-r4JIya8Ssr6-DswY4'  # This is my test spreadsheet

    # Set room mapping
    room_mapping = dr.room_mapping

    # Set query options
    sheet_options = [
        'Mon 2/13', 'Tues 2/14', 'Wed 2/15', 'Thurs 2/16', 'Fri 2/17',
        'Mon 2/20', 'Tues 2/21', 'Wed 2/22', 'Thurs 2/23', 'Fri 2/24',
        'Mon 2/27', 'Tues 2/28', 'Wed 3/1', 'Thurs 3/2', 'Fri 3/3'
        ]

    # Determine which day to send for
    today = time.localtime()
    month = today.tm_mon
    day = today.tm_mday
    if month == 2 and day == 28:
        match_day = '3/1'
    elif month == 2 and day < 13:
        match_day = '2/13'
    else:
        match_day = str(month) + '/' + str(day + 1)

    if specific_day:
        match_day = specific_day

    # Pick out the appropriate sheet names from the list
    sheet_names = [x for x in sheet_options if match_day in x]

    full_range = dr.full_range

    if team is None:
        name_dict = {
            "alice": [],
            "brainspec": [],
            "brizi": [],
            "care": [],
            "evolve": [],
            "lorem": [],
            "nix": [],
            "offgridbox": [],
            "rate": [],
            "sea machines": [],
            "solstice": [],
            "tive": [],
            "voatz": [],
            'andrew': [],
            'ashley': [],
            'dan': [],
            'dmitriy': [],
            'justin': [],
            'keaton': [],
            'lillian': [],
            'max': [],
            'miranda': [],
            'troy': [],
            'yada': []
        }
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
        csv_name = day_to_filename(day)

        # Make request for sheet
        sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_query).execute()
        new_sheet = sheet['values']
        new_sheet = new_sheet[1:]  # Get rid of the header row
        for idx, new_sheet_row in enumerate(new_sheet):
            if len(new_sheet_row) < 19:
                new_sheet[idx].extend([''] * (19 - len(new_sheet_row)))

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
                    name = email_sender.process_name(row[col_num])
                    if name and name != 'not_found' and name in name_dict.keys():
                        new_event_dict = {'time': timeslot, 'mentor': mentor_name,
                                          'room_num': str(room_num), 'room_name': room_name, 'day': day}
                        name_dict[name].append(new_event_dict)

        print('Got info for ' + day)

    if send_emails:
        email_sender.send_daily_mail(name_dict)
        return None
    else:
        return name_dict


def day_to_filename(day):
    csv_name = day.replace(' ', '_').replace('/', '_') + '.csv'
    csv_name = '/cached_schedules/' + csv_name
    dirname = os.path.dirname(__file__)
    csv_name = dirname + csv_name
    return csv_name


if __name__ == '__main__':
    main()

import csv

from httplib2 import Http

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import directories as dr

LOCAL_PATH = "/Users/keatonarmentrout/Desktop/Techstars/Mentor Madness/"

def main():
    """
    This function accesses the sheets for each day of Mentor Madness and ONLY SAVES THEM.

    This DOES NOT do any comparisons or alerts.
    """
    # Get credentials from Google Developer Console
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    secret_key_json = LOCAL_PATH + 'MM Bot-32fa78cfd51b.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(secret_key_json, scopes=scopes)

    # Authenticate using Http object
    http_auth = credentials.authorize(Http())

    # Build Google API response object for sheets
    sheets_api = build('sheets', 'v4', credentials=credentials)

    # Set spreadsheet ID
    spreadsheet_id = '18gb1ehs9-hmXbIkKaTcLUvurzAJzpjDiXgNFZeazrNA'  # This is the MM spreadsheet
    # spreadsheet_id = '1qdAgkuyAl6DRV3LRn-zheWSiD-r4JIya8Ssr6-DswY4'  # This is my test spreadsheet

    # Set query options
    week1 = ['Mon 2/13', 'Tues 2/14', 'Wed 2/15', 'Thurs 2/16', 'Fri 2/17']
    week2 = ['Mon 2/20', 'Tues 2/21', 'Wed 2/22', 'Thurs 2/23', 'Fri 2/24']
    week3 = ['Mon 2/27', 'Tues 2/28', 'Wed 3/1', 'Thurs 3/2', 'Fri 3/3']

    small_sheet_names = [
        'Mon 2/13']

    # Determine which days to check for
    sheet_names = week3
    sheet_names = week2
    sheet_names = week1

    full_range = dr.full_range

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range
        csv_name = day_to_filename(day)

        # Make request for sheet
        sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_query).execute()
        content = sheet['values']
        for idx, new_sheet_row in enumerate(content):
            if len(new_sheet_row) < 19:
                content[idx].extend([''] * (19 - len(new_sheet_row)))

        # Save the sheet
        with open(csv_name, 'w') as file:
            writer = csv.writer(file)
            writer.writerows(content)

        print('Saved ' + day)


def day_to_filename(day):
    csv_name = day.replace(' ', '_').replace('/', '_') + '.csv'
    csv_name = 'cached_schedules/' + csv_name
    return csv_name


if __name__ == '__main__':
    main()

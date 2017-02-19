import time
import csv
import os
import pandas as pd

from . import directories as dr
from .email_sender import *
from . import utils


def add_booking(raw_json):
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    meeting = utils.parse_webhook_json(raw_json)

    # Set spreadsheet ID
    spreadsheet_id = utils.spreadsheet_id  # This is the MM spreadsheet
    # spreadsheet_id = '1qdAgkuyAl6DRV3LRn-zheWSiD-r4JIya8Ssr6-DswY4'  # This is my test spreadsheet

    # Set room mapping
    room_mapping = utils.room_mapping

    # Set query options
    sheet_options = utils.sheet_options

    # Set day to retrieve
    sheet_names = [x for x in sheet_options if meeting['day'] in x]
    if not sheet_names:
        # TODO: Implement some sort of error notification. Maybe email.
        return

    if len(sheet_names) > 1:
        sheet_names = sheet_names[0]

    # Get the range of times to look at
    start_bound = utils.spreadsheet_time_mapping.get(meeting['start_time'])
    end_bound = utils.spreadsheet_time_mapping.get(meeting['end_time'])

    cell_range = utils.start_col + start_bound + ':' + utils.end_col + end_bound

    # Make request for sheet
    sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=cell_range).execute()
    new_sheet = sheet['values']

    # Pad sheet to be the appropriate length in each row
    for idx, new_sheet_row in enumerate(new_sheet):
        if len(new_sheet_row) < utils.row_length:
            new_sheet[idx].extend([''] * (utils.row_length - len(new_sheet_row)))

    # Make sheet into dataframe
    sheet_df = pd.DataFrame(data=new_sheet, columns=utils.headers)





    row_counter = 0
    for old_row in reader:
        # print(old_row)
        new_row = new_sheet[row_counter]
        timeslot = new_row[0]

        # Make rows the same length if they are not
        if len(old_row) < len(new_row):
            old_row.extend([''] * (len(new_row) - len(old_row)))
        elif len(old_row) > len(new_row):
            new_row.extend([''] * (len(old_row) - len(new_row)))

        # Iterate over rooms
        for room_num in range(1, len(room_mapping.keys()) + 1):
            # Get descriptive variables of room
            room_dict = room_mapping[room_num]
            room_name = room_dict['name']
            mentor_name = new_row[room_dict['mentor_col']]

            for col_num in room_dict['check_range']:
                old_name = old_row[col_num]
                new_name = new_row[col_num]
                if new_name != old_name:
                    new_event_dict = {'time': timeslot, 'name': new_name, 'mentor': mentor_name,
                                      'room_num': str(room_num), 'room_name': room_name, 'day': day}
                    old_event_dict = {'time': timeslot, 'name': old_name, 'mentor': mentor_name,
                                      'room_num': str(room_num), 'room_name': room_name, 'day': day}

                    if new_name and old_name:
                        # Someone was changed, assuming the names are different
                        if process_name(new_name) != process_name(old_name):
                            deleting_msgs.append(old_event_dict)
                            adding_msgs.append(new_event_dict)
                        else:
                            continue
                    elif old_name:
                        # Someone was deleted
                        deleting_msgs.append(old_event_dict)
                    elif new_name:
                        # Someone was added
                        adding_msgs.append(new_event_dict)

        row_counter += 1


def remove_booking(raw_json):
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    meeting_dict = utils.parse_webhook_json(raw_json)


def change_booking(raw_json):
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    meeting_dict = utils.parse_webhook_json(raw_json)


def main():
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    # Set spreadsheet ID
    spreadsheet_id = utils.spreadsheet_id  # This is the MM spreadsheet
    # spreadsheet_id = '1qdAgkuyAl6DRV3LRn-zheWSiD-r4JIya8Ssr6-DswY4'  # This is my test spreadsheet

    # Set room mapping
    room_mapping = utils.room_mapping

    # Set query options
    sheet_options = utils.sheet_options
    sheet_names = [sheet_options[day_index]]

    full_range = utils.full_range

    # Create holding variables for adding and deleting messages
    adding_msgs = []
    deleting_msgs = []

    for day in sheet_names:
        # String formatting for API query and file saving
        sheet_query = day + '!' + full_range
        csv_name = day_to_filename(day)

        # Make request for sheet
        sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_query).execute()
        new_sheet = sheet['values']
        for idx, new_sheet_row in enumerate(new_sheet):
            if len(new_sheet_row) < 19:
                new_sheet[idx].extend([''] * (19 - len(new_sheet_row)))

        # Load old sheet
        old_sheet = open(csv_name, 'r')
        reader = csv.reader(old_sheet)

        row_counter = 0
        for old_row in reader:
            # print(old_row)
            new_row = new_sheet[row_counter]
            timeslot = new_row[0]

            # Make rows the same length if they are not
            if len(old_row) < len(new_row):
                old_row.extend([''] * (len(new_row) - len(old_row)))
            elif len(old_row) > len(new_row):
                new_row.extend([''] * (len(old_row) - len(new_row)))

            # Iterate over rooms
            for room_num in range(1, len(room_mapping.keys()) + 1):
                # Get descriptive variables of room
                room_dict = room_mapping[room_num]
                room_name = room_dict['name']
                mentor_name = new_row[room_dict['mentor_col']]

                for col_num in room_dict['check_range']:
                    old_name = old_row[col_num]
                    new_name = new_row[col_num]
                    if new_name != old_name:
                        new_event_dict = {'time': timeslot, 'name': new_name, 'mentor': mentor_name,
                                          'room_num': str(room_num), 'room_name': room_name, 'day': day}
                        old_event_dict = {'time': timeslot, 'name': old_name, 'mentor': mentor_name,
                                          'room_num': str(room_num), 'room_name': room_name, 'day': day}

                        if new_name and old_name:
                            # Someone was changed, assuming the names are different
                            if process_name(new_name) != process_name(old_name):
                                deleting_msgs.append(old_event_dict)
                                adding_msgs.append(new_event_dict)
                            else:
                                continue
                        elif old_name:
                            # Someone was deleted
                            deleting_msgs.append(old_event_dict)
                        elif new_name:
                            # Someone was added
                            adding_msgs.append(new_event_dict)

            row_counter += 1

        # Save the sheet
        old_sheet.close()
        old_sheet = open(csv_name, 'w')
        writer = csv.writer(old_sheet)
        writer.writerows(new_sheet)

    # send_update_mail(adding_msgs, deleting_msgs)


def day_to_filename(day):
    csv_name = day.replace(' ', '_').replace('/', '_') + '.csv'
    csv_name = '/cached_schedules/' + csv_name
    dirname = os.path.dirname(__file__)
    csv_name = dirname + csv_name
    return csv_name


if __name__ == '__main__':
    main()
    print('Ran successfully')

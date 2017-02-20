import csv
import os
import numpy as np

from . import directories as dr
from .email_sender import *
from . import utils


def add_booking(raw_json):
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    meeting = utils.parse_webhook_json(raw_json)

    # Set spreadsheet ID
    # spreadsheet_id = utils.spreadsheet_id  # This is the MM spreadsheet
    spreadsheet_id = '1qdAgkuyAl6DRV3LRn-zheWSiD-r4JIya8Ssr6-DswY4'  # This is my test spreadsheet

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

    day = sheet_names[0]

    # Get the range of times to look at
    cell_range = utils.make_cell_range(meeting['start_time'], meeting['end_time'])
    range_query = day + '!' + cell_range

    # Make request for sheet
    sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_query).execute()
    new_sheet = sheet['values']

    # Pad sheet to be the appropriate length in each row
    for idx, new_sheet_row in enumerate(new_sheet):
        if len(new_sheet_row) < utils.row_length:
            new_sheet[idx].extend([''] * (utils.row_length - len(new_sheet_row)))

    # Make sheet into dataframe
    sheet_np = np.asarray(new_sheet)

    # Check to see if there is an entirely free block of time.
    # If so, fill the mentor in completely.
    found_free_block = False
    for mentor_col_num in utils.mentor_columns:
        if not any(x for x in sheet_np[:, mentor_col_num]):
            for row_idx in range(0, len(new_sheet)):
                new_sheet[row_idx][mentor_col_num] = meeting['name']
            found_free_block = True
            break

    # If there is not a completely free block, fill in by row
    # I'm iterating over the normal python lists now (not df)
    if not found_free_block:
        for row in new_sheet:
            # If there is a blank mentor column, fill it in
            appnd = True
            for x in utils.mentor_columns:
                if not row[x]:
                    row[x] = meeting['name']
                    appnd = False
                    break

            # If the end is reached, append to the last mentor column
            # TODO: Add an alert if this happens
            if appnd:
                row[utils.mentor_columns[-1]] += ', ' + meeting['name']

    # Update the spreadsheet
    update_body = {
        'values': new_sheet
    }

    # Update the sheet
    result = sheets_api.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_query,
        valueInputOption=utils.value_input_option, body=update_body).execute()

    # Run the update script for that day
    # TODO: make the update script take input arguments for specific days

    return True


def remove_booking(raw_json):
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    meeting_dict = utils.parse_webhook_json(raw_json)


def change_booking(raw_json):
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    meeting_dict = utils.parse_webhook_json(raw_json)


def main():

    # Set query options
    sheet_options = utils.sheet_options
    sheet_names = [sheet_options[0]]

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
            new_row = new_sheet[row_counter]
            timeslot = new_row[0]

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

            row_counter += 1

        # Save the sheet
        old_sheet.close()
        old_sheet = open(csv_name, 'w')
        writer = csv.writer(old_sheet)
        writer.writerows(new_sheet)


def day_to_filename(day):
    csv_name = day.replace(' ', '_').replace('/', '_') + '.csv'
    csv_name = '/cached_schedules/' + csv_name
    return csv_name


if __name__ == '__main__':
    main()
    print('Ran successfully')

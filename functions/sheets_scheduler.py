import os
import numpy as np

from . import directories as dr
from . import utils


def add_booking(raw_json):
    # Get info
    info_dict = booking_setup(raw_json=raw_json)
    new_sheet = info_dict['new_sheet']
    meeting = info_dict['meeting']

    # Make sheet into numpy array
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

    info_dict['new_sheet'] = new_sheet
    return update_google_sheet(**info_dict)


def remove_booking(raw_json, custom_range=None):
    # Get info
    info_dict = booking_setup(raw_json=raw_json, custom_range=custom_range)
    new_sheet = info_dict['new_sheet']
    meeting = info_dict['meeting']

    # Add a space to the beginning of last name to avoid finding it within
    # other words
    last_name = ' ' + meeting.get('last_name')
    first_name = meeting.get('first_name')

    # Make sheet into numpy array
    sheet_np = np.asarray(new_sheet)

    # Transpose so columns become rows (faster)
    sheet_np = np.transpose(sheet_np)

    # Remove the mentor from the
    for mentor_col_num in utils.mentor_columns:
        if last_name:
            if any(last_name in x for x in sheet_np[mentor_col_num, :]):
                # Check for both first and last name
                sheet_np[mentor_col_num, :] = ['' if last_name and first_name in y else y for y in sheet_np[mentor_col_num, :]]
        else:
            # If I only have the first name, make a note that it could be cancelled, instead of just cancelling outright.
            if any(first_name in x for x in sheet_np[mentor_col_num, :]):
                sheet_np[mentor_col_num, :] = [y + ' CANCELLED?' if first_name in y else y for y in sheet_np[mentor_col_num, :]]

    sheet_np = np.transpose(sheet_np)
    new_sheet = sheet_np.tolist()

    info_dict['new_sheet'] = new_sheet
    return update_google_sheet(**info_dict)


def change_booking(raw_json):
    # Two-step process: remove previous booking and add new booking.
    remove_booking(raw_json, custom_range=utils.full_range)
    return add_booking(raw_json)


def booking_setup(raw_json, custom_range=None):
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

    day = sheet_names[0]

    # Get the range of times to look at
    if custom_range is None:
        cell_range = utils.make_cell_range(meeting['start_time'], meeting['end_time'])
    else:
        cell_range = custom_range
    range_query = day + '!' + cell_range

    # Make request for sheet
    sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_query).execute()
    new_sheet = sheet['values']

    # Pad sheet to be the appropriate length in each row
    for idx, new_sheet_row in enumerate(new_sheet):
        if len(new_sheet_row) < utils.row_length:
            new_sheet[idx].extend([''] * (utils.row_length - len(new_sheet_row)))

    return_dict = {
        'new_sheet': new_sheet,
        'spreadsheet_id': spreadsheet_id,
        'range_query': range_query,
        'meeting': meeting,
        'sheets_api': sheets_api
    }

    return return_dict


def update_google_sheet(**kwargs):
    # Update the spreadsheet
    update_body = {
        'values': kwargs.get('new_sheet')
    }

    # Update the sheet
    sheets_api = kwargs.get('sheets_api')
    result = sheets_api.spreadsheets().values().update(
        spreadsheetId=kwargs.get('spreadsheet_id'), range=kwargs.get('range_query'),
        valueInputOption=utils.value_input_option, body=update_body).execute()

    # Run the update script for that day
    # TODO: make the update script take input arguments for specific days

    return True

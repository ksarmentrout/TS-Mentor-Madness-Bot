import datetime
import os
import re

from functions.utilities import variables as vrs
from functions.utilities import directories as dr
from functions.utilities import utils
from database import db_interface as db

os.environ['mm_bot_gmail_name'] = vrs.mm_bot_gmail_name
os.environ['mm_bot_gmail_password'] = vrs.mm_bot_gmail_password


def add_cal_events(meeting_dict, cal_api=None):
    """

    :param meeting_dict: dict where key = name, value = list of Meeting objects
    :param cal_api: calendar api object
    :return:
    """
    if cal_api is None:
        cal_api = utils.google_calendar_login()

    for name, meeting in meeting_dict.iteritems():
        try:
            # Get the company name and associate name
            # names = []
            # if meeting.company:
            #     names.append(meeting.company)
            # if meeting.associate:
            #     names.append(meeting.associate)

            # If meeting already exists, don't recreate it.
            meeting_exists = check_for_cal_event(meeting, name)
            if meeting_exists:
                continue

            cal_id = dr.calendar_id_dir[name]

            start_time = meeting.start_time
            time_range = utils.make_time_range(start_time)
            time_range = time_range.replace(' ', '')

            meeting_text = 'Meeting with ' + meeting['mentor'] + ' in Room ' + meeting['room_num']  + \
                           ' (' + meeting['room_name'] + ') on ' + meeting['day'] + ' ' + time_range

            # Create the event on the appropriate calendar.
            created_event = cal_api.events().quickAdd(calendarId=cal_id, text=meeting_text).execute()
            meeting.cal_event_id = created_event.id

            print('created event: ' + created_event['summary'])
        except:
            continue

    # Add IDs to saved database versions
    db.add_meeting_cal_event_ids(meeting_dict)


def delete_cal_events(meeting_dict, cal_api=None):
    if cal_api is None:
        cal_api = utils.google_calendar_login()

    for name, meetings in meeting_dict.iteritems():
        for meeting in meetings:
            try:
                meeting_id = check_for_cal_event(meeting, name, return_event_id=True)
                if meeting_id:
                    name = meeting.get('name')
                    if not name:
                        continue
                    name = utils.process_name(name)
                    cal_id = dr.calendar_id_dir[name]

                    # Delete event
                    deleted_event = cal_api.events().delete(calendarId=cal_id, eventId=meeting_id).execute()
                    print('deleted event: ' + deleted_event['summary'])
            except:
                continue


def update_cal_events(added_msg_dicts, deleted_msg_dicts):
    cal_api = utils.google_calendar_login()

    # Add and delete calendar events
    add_cal_events(added_msg_dicts, cal_api)
    delete_cal_events(deleted_msg_dicts, cal_api)


def check_for_cal_event(meeting, name, return_event_id=False):
    # First, check that there is a calendar associated with the name
    cal_id = dr.calendar_id_dir[name]
    if not cal_id:
        return False if return_event_id else None

    # Get the saved Meeting object
    saved_meeting = db.get_saved_meeting(meeting)

    # Check if name is associate or company
    # and look for the appropriate event ID
    event_id = None
    if name == saved_meeting.company:
        event_id = saved_meeting.company_cal_event_id
    elif name == saved_meeting.associate:
        event_id = saved_meeting.associate_cal_event_id

    event_exists = False
    if event_id:
        event_exists = True

    # Return the appropriate variable
    if return_event_id:
        return event_id
    else:
        return event_exists


def booking_setup(raw_json, custom_range=None):
    """
    Left over from previous implementation

    :param raw_json:
    :param custom_range:
    :return:
    """
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    meeting = utils.parse_webhook_json(raw_json)

    # Set spreadsheet ID
    spreadsheet_id = vrs.spreadsheet_id

    # Set query options
    sheet_options = vrs.sheet_options

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
    sheet_query = day + '!' + cell_range

    # Get the sheet
    new_sheet = utils.get_sheet(sheets_api, spreadsheet_id=spreadsheet_id, sheet_query=sheet_query)

    return_dict = {
        'new_sheet': new_sheet,
        'spreadsheet_id': spreadsheet_id,
        'range_query': sheet_query,
        'meeting': meeting,
        'sheets_api': sheets_api
    }

    return return_dict

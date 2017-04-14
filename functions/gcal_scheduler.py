import datetime
import os
import re

from functions.utilities import variables as vrs
from functions.utilities import directories as dr
from functions.utilities import utils

os.environ['mm_bot_gmail_name'] = vrs.mm_bot_gmail_name
os.environ['mm_bot_gmail_password'] = vrs.mm_bot_gmail_password


def booking_setup(raw_json, custom_range=None):
    # Build Google API response object for sheets
    sheets_api = utils.google_sheets_login()

    meeting = utils.parse_webhook_json(raw_json)

    # Set spreadsheet ID
    spreadsheet_id = vrs.spreadsheet_id

    # Set room mapping
    room_mapping = vrs.room_mapping

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


def main():
    cal_api = utils.google_calendar_login()

    calendar_list = cal_api.calendarList().list(showHidden=True).execute()
    # print(calendar_list)
    # for calendar_list_entry in calendar_list['items']:
    #     print(calendar_list_entry['summary'])

    cal_id = 'cs6ctbvacn0nq68qgf3ofsffh8@group.calendar.google.com'

    # created_event = cal_api.events().quickAdd(
    #     calendarId=cal_id,
    #     text='Meeting with Joe Caruso in Room 1 (Glacier) on Tues 2/21 10am-10:30am').execute()

    events = cal_api.events().list(calendarId=cal_id, q='Meeting with').execute()
    for event in events['items']:
        print(event)


def add_cal_events(event_list, cal_api=None):
    if cal_api is None:
        cal_api = utils.google_calendar_login()

    for meeting in event_list:
        # If meeting already exists, don't recreate it.
        meeting_exists = check_for_cal_event(cal_api, meeting)
        if meeting_exists:
            continue

        # Get info for the event
        name = meeting.get('name')
        if not name:
            continue
        name = utils.process_name(name)

        cal_id = dr.calendar_id_dir[name]

        start_time = meeting['time']
        time_range = utils.make_time_range(start_time)
        time_range = time_range.replace(' ', '')

        meeting_text = 'Meeting with ' + meeting['mentor'] + ' in Room ' + meeting['room_num']  + \
                       ' (' + meeting['room_name'] + ') on ' + meeting['day'] + ' ' + time_range

        # Create the event on the appropriate calendar.
        created_event = cal_api.events().quickAdd(calendarId=cal_id, text=meeting_text).execute()
        print('created event: ' + created_event['summary'])


def delete_cal_events(event_list, cal_api=None):
    if cal_api is None:
        cal_api = utils.google_calendar_login()

    for meeting in event_list:
        event_id = check_for_cal_event(cal_api, meeting, return_event_id=True)
        if event_id:
            name = meeting.get('name')
            if not name:
                continue
            name = utils.process_name(name)
            cal_id = dr.calendar_id_dir[name]

            # Delete event
            deleted_event = cal_api.events().delete(calendarId=cal_id, eventId=event_id).execute()
            print('deleted event: ' + deleted_event['summary'])


def update_cal_events(added_msg_dicts, deleted_msg_dicts):
    cal_api = utils.google_calendar_login()

    # Send mail
    add_cal_events(added_msg_dicts, cal_api)
    delete_cal_events(deleted_msg_dicts, cal_api)


def check_for_cal_event(cal_api, meeting, return_event_id=False):
    name = meeting.get('name')
    if not name:
        return False if return_event_id else None

    name = utils.process_name(name)

    cal_id = dr.calendar_id_dir[name]
    if not cal_id:
        return False if return_event_id else None

    # Fix time in order to compare
    # Get current year
    today = datetime.date.today()
    year = str(today.year)

    # Get the meeting day and month
    m = re.search('([0-9]{1,2})/([0-9]{2})', meeting['day'])
    if not m:
        return False if return_event_id else None

    month = m.group(1)
    day = m.group(2)
    if len(month) == 1:
        month = '0' + month

    # Get the meeting day and time
    start_time = meeting['time']
    start_time = start_time[:start_time.find(' ')]
    if len(start_time) == 4:
        start_time = '0' + start_time

    comparison_time = year + '-' + month + '-' + day + 'T' + start_time

    events = cal_api.events().list(calendarId=cal_id, q='Meeting with').execute()
    event_exists = False
    target_event_id = None
    for event in events['items']:
        st_time = event['start']['dateTime']
        txt = event['summary']

        # Check that the start time and the mentor name match the event
        if comparison_time in st_time:
            event_exists = True
            target_event_id = event['id']
            break

    if return_event_id:
        return target_event_id
    else:
        return event_exists


if __name__ == '__main__':
    # main()
    test_event = [{'day': 'Mon 2/20', 'mentor': 'Joe Caruso, Bantam', 'name': 'keaton', 'room_name': 'Harbor', 'room_num': '2', 'time': '9:30 AM'}]
    delete_cal_events(test_event)

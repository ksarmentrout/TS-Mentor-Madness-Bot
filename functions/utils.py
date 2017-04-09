"""
~ NOTES ~

directories.py is for email and Google Calendar DICTIONARIES.
utils.py is for FUNCTIONS
variables.py is for OTHER VARIABLES (mostly for Google Sheets)
"""

import re
import os
from datetime import datetime, timedelta
import time

from httplib2 import Http
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import directories as dr
import variables as vrs


def parse_webhook_json(added_json):
    ad = added_json
    ad['name'] = ad.get('first_name') + ' ' + ad.get('last_name')
    time_dict = parse_time(ad)
    ad.update(**time_dict)

    return ad


def parse_time(original_dict):
    time_dict = {}
    start_field = original_dict['start_time']
    end_field = original_dict['end_time']

    # Get the day
    day = re.search('([0-9]{1,2}/[0-9]{1,2})/', start_field)
    if not day:
        return {}

    time_dict['day'] = day.group(1)

    # Get the start and end times
    start_time = re.search('\s([0-9]{1,2}:[0-9]{2})', start_field)
    time_dict['start_time'] = start_time.group(1)

    end_time = re.search('\s([0-9]{1,2}:[0-9]{2})', end_field)
    time_dict['end_time'] = end_time.group(1)

    return time_dict


def google_sheets_login():
    # Get credentials from Google Developer Console
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    json_path = vrs.LOCAL_PATH + "scheduling_bot/MM-Scheduler-61cb94ec8350.json"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scopes=scopes)

    # Authenticate using Http object
    http_auth = credentials.authorize(Http())

    # Build Google API response object for sheets
    sheets_api = build('sheets', 'v4', http=http_auth)

    return sheets_api


def google_calendar_login():
    # Get credentials from Google Developer Console
    scopes = ['https://www.googleapis.com/auth/calendar']

    # NOTE: The 'MM-Scheduler' service account is owned by mentor.madness.bot@gmail.com
    json_path = vrs.LOCAL_PATH + "scheduling_bot/MM-Scheduler-61cb94ec8350.json"
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scopes=scopes)

    # Authenticate using Http object
    http_auth = credentials.authorize(Http())

    # Build Google API response object for sheets
    sheets_api = build('calendar', 'v3', http=http_auth)

    return sheets_api


def make_cell_range(start_time, end_time):
    start_bound = vrs.spreadsheet_time_mapping.get(start_time)
    end_bound = vrs.spreadsheet_time_mapping.get(end_time)
    end_bound = str(int(end_bound) - 1)
    cell_range = vrs.start_col + start_bound + ':' + vrs.end_col + end_bound
    return cell_range


def make_time_range(start_time):
    # Creates a half-hour time window based on the start time

    # Pads with zero
    if len(start_time[:start_time.find(' ')]) == 4:
        start_time = '0' + start_time

    # Shifts to 24-hour clock
    if 'PM' in start_time and start_time[:2] != '12':
        hour = int(start_time[:2])
        hour = str(hour + 12)
        start_time = hour + start_time[2:]

    start_time = start_time[:start_time.find(' ')]

    start_obj = datetime.strptime(start_time, '%H:%M')
    end_obj = start_obj + timedelta(minutes=30)
    end_time = end_obj.strftime('%H:%M')

    time_range = start_time + '-' + end_time
    return time_range


def get_next_day():
    # TODO: make this general
    today = time.localtime()
    month = today.tm_mon
    day = today.tm_mday

    # Handle the end of February
    if month == 2 and day == 28:
        match_day = '3/1'
    # Handle before the beginning of MM
    elif month == 2 and day < 13:
        match_day = '2/13'
    else:
        match_day = str(month) + '/' + str(day + 1)
    return match_day


def day_to_filename(day):
    csv_name = day.replace(' ', '_').replace('/', '_') + '.csv'
    csv_name = '/cached_schedules/' + csv_name
    csv_name = vrs.LOCAL_PATH + csv_name
    return csv_name


def process_name(original_name):
    # ALL CASES need to be checked because sometimes other information
    # besides just the name goes into these boxes. I know it's ugly.
    name = original_name.lower()
    if 'rate' in name:
        name = 'rate'
    elif 'alice' in name:
        name = 'alice'
    elif 'care' in name:
        name = 'care'
    elif 'machine' in name:
        name = 'sea machines'
    elif name.strip() == 'sea':
        name = 'sea machines'
    elif 'brain' in name:
        name = 'brainspec'
    elif 'brizi' in name:
        name = 'brizi'
    elif 'evolve' in name:
        name = 'evolve'
    elif 'lorem' in name:
        name = 'lorem'
    elif 'nix' in name:
        name = 'nix'
    elif 'offgrid' in name:
        name = 'offgridbox'
    elif 'solstice' in name:
        name = 'solstice'
    elif 'tive' in name:
        name = 'tive'
    elif 'voatz' in name:
        name = 'voatz'
    elif 'ashley' in name:
        name = 'ashley'
    elif 'andrew' in name:
        name = 'andrew'
    elif 'dmitriy' in name:
        name = 'dmitriy'
    elif 'dimitry' in name:
        name = 'dmitriy'
    elif 'justin' in name:
        name = 'justin'
    elif 'keaton' in name:
        name = 'keaton'
    elif 'lillian' in name:
        name = 'lillian'
    elif 'lilian' in name:
        name = 'lillian'
    elif 'troy' in name:
        name = 'troy'
    elif 'yada' in name:
        name = 'yada'
    elif 'max' in name:
        name = 'max'
    elif 'dan' in name:
        name = 'dan'
    elif 'miranda' in name:
        name = 'miranda'
    else:
        name = 'not_found'
    return name

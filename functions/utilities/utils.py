"""
~ NOTES ~

directories.py is for email and Google Calendar DICTIONARIES.
utils.py is for FUNCTIONS
variables.py is for OTHER VARIABLES (mostly for Google Sheets)
"""

import datetime
import re
from collections import OrderedDict

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

from functions.utilities import variables as vrs
from functions.utilities import directories as dr


def parse_webhook_json(added_json):
    ad = added_json
    ad['name'] = ad.get('first_name') + ' ' + ad.get('last_name')
    time_dict = _parse_time_from_webhook_json(ad)
    ad.update(**time_dict)

    return ad


def _parse_time_from_webhook_json(original_dict):
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


def get_sheet(sheets_api, spreadsheet_id, sheet_query):
    # Check that inputs exist
    for x in [sheets_api, spreadsheet_id, sheet_query]:
        if not x:
            raise KeyError('Invalid input to utils.get_sheet(): ' + str(x))

    # Make request for sheet
    sheet = sheets_api.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_query).execute()
    new_sheet = sheet['values']

    # Make sure all rows from CSV are the same length
    for idx, new_sheet_row in enumerate(new_sheet):
        if len(new_sheet_row) < vrs.row_length:
            new_sheet[idx].extend([''] * (vrs.row_length - len(new_sheet_row)))

    return new_sheet


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

    start_obj = datetime.datetime.strptime(start_time, '%H:%M')
    end_obj = start_obj + datetime.timedelta(minutes=30)
    end_time = end_obj.strftime('%H:%M')

    time_range = start_time + '-' + end_time
    return time_range


def get_next_day():
    """
    Gets the next business day.
    :return: Date of next business day in format 'mm/dd'
    """
    today = datetime.date.today()
    month = today.month
    day = today.day

    # Get next business day
    if today.isoweekday() in (5, 6, 7):
        today += datetime.timedelta(days=8 - today.isoweekday())
    else:
        today += datetime.timedelta(1)

    match_day = str(month) + '/' + str(day)
    return match_day


def get_next_week():
    today = datetime.date.today()
    week_num = today.isocalendar()[1]
    next_week = week_num + 1

    # Get the weeks
    week_lists = vrs.week_lists

    # Get the first day of each week
    first_days = [x[0] for x in week_lists]

    # Get the mm/dd date in each first day
    first_days = [x[x.find(' ')+1:] for x in first_days]

    # Parse the dates
    first_day_objs = [datetime.datetime.strptime(x, '%m/%d') for x in first_days]

    # Find the week numbers for each week
    week_numbers = [x.isocalendar()[1] for x in first_day_objs]

    # Find the week following the current week
    if next_week in week_numbers:
        return week_lists[week_numbers.index(next_week)]
    else:
        return None


def get_today(skip_weekends=False):
    today = datetime.date.today()
    month = today.month
    day = today.day

    if skip_weekends:
        # Get next business day
        if today.isoweekday() in (6, 7):
            today += datetime.timedelta(days=8 - today.isoweekday())

    match_day = str(month) + '/' + str(day)
    return match_day


def parse_timeslot(timeslot):
    return timeslot


def day_to_filename(day):
    csv_name = day.replace(' ', '_').replace('/', '_') + '.csv'
    csv_name = '/cached_schedules/' + csv_name
    csv_name = vrs.LOCAL_PATH + csv_name
    return csv_name


def get_proper_name(original_name):
    return dr.names_to_proper_names.get(original_name, original_name)


def format_day_picked(day):
    """
    This is for going from the format of the day chosen on the dashboard
    into the format used for the Google Sheets tabs.

    The day is given as (for example) 'Thu 9/21/2017'.
    The sheets are styled as 'Thu 9/21'.

    I could just cut off the '/2017' but I'm using datetime for
    consistency and flexibility.

    :param day: str,
    :return: string
    """
    # Parse the days
    picked_day = datetime.datetime.strptime(day, '%a %m/%d/%Y')

    # I'm using this instead of strftime to prevent 0-padded days
    sheet_day = '{dy:%a} {dy.month}/{dy.day}'.format(dy=picked_day)
    return sheet_day


def format_week_picked(week):
    """
    The week is given as (for example) 'Sun 4/09/2017 - Sat 4/15/2017'.
    It lists the Saturday and the Sunday, so this function returns the
    week (list of days) containing the included Monday.

    :param week:
    :return:
    """
    # Parse the days
    day_bounds = week.split(' - ')
    days = [datetime.datetime.strptime(day, '%a %m/%d/%Y') for day in day_bounds]

    # Get the Monday within this week
    sunday = days[0]
    monday = sunday + datetime.timedelta(days=1)

    # Parse the Monday
    sheet_monday = '{dy:%a} {dy.month}/{dy.day}'.format(dy=monday)

    selected_week = [x for x in vrs.week_lists if sheet_monday in x]

    if len(selected_week) > 1:
        raise IndexError('Multiple weeks returned from the week selected. Error in vrs.week_lists?')

    return selected_week[0]


def get_name_type(name):
    """

    :param name:
    :return: str, either "associate" or "company"
    """
    if name in dr.company_name_list:
        name_type = 'company'
    elif name in dr.associate_name_list:
        name_type = 'associate'
    else:
        name_type = 'mentor'

    return name_type


def associate_and_company_meetings_dict(meetings):
    # Make the associate and company dictionaries s.t. they're sorted
    associate_meetings = OrderedDict()
    company_meetings = OrderedDict()

    for associate in dr.associate_proper_names:
        if meetings[associate]:
            associate_meetings[associate] = meetings[associate]

    for company in dr.company_proper_names:
        if meetings[company]:
            company_meetings[company] = meetings[company]

    there_are_associates = False
    there_are_companies = False
    if len(associate_meetings) >= 1:
        there_are_associates = True
    if len(company_meetings) >= 1:
        there_are_companies = True

    meetings_dict = {
        'there_are_associates': there_are_associates,
        'there_are_companies': there_are_companies,
        'associate_meetings': associate_meetings,
        'company_meetings': company_meetings
    }
    return meetings_dict


def process_name(original_name):
    """
    ALL CASES need to be checked because sometimes other information
    besides just the name goes into these boxes. I know it's ugly.

    :param original_name: string value pulled from Google Sheet
    :return:
    """
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

import traceback

import email_sender
from exceptions import *
from database import db_interface as db
from functions.utilities import utils as utils
from functions.utilities import variables as vrs
from functions.utilities import directories as dr


def get_meeting_views(name, specific_date=None, daily_or_weekly=None):
    """
    Returns a dictionary for meetings, where keys are names
    and values are meeting lists.
    This is for displaying the meetings on the /view_schedule page
    :param name: str
    :param specific_date: str, date in format (for example) "Thu 9/21"
    :param daily_or_weekly: str, either "daily" or "weekly"
    :return:
    """
    # Add all the meetings
    try:
        meeting_dict = meeting_retrieval(
            name=name,
            specific_date=specific_date,
            daily_or_weekly=daily_or_weekly
        )
    except DateNotFoundError as exc:
        print(exc.args)
        raise IndexError(exc.args[0])

    return meeting_dict


def email_meetings(name, specific_date=None, daily_or_weekly=None):
    """
    Sends emails to every recipient specified by the "name" input variable
    with their schedule for the day(s) specified by the "specific_date"
    and/or "daily_or_weekly" input variables.

    :param name:
    :param specific_date: str, date in format (for example) "Thu 9/21"
    :param daily_or_weekly: str, either "daily" or "weekly"
    :return:
    """
    try:
        meeting_dict = meeting_retrieval(
            name=name,
            specific_date=specific_date,
            daily_or_weekly=daily_or_weekly
        )
    except DateNotFoundError as exc:
        raise DateNotFoundError(exc)

    try:
        email_sender.send_daily_mail(meeting_dict)
    except Exception:
        traceback.print_exc()
        raise EmailError('Could not send daily mail.')


def meeting_retrieval(name, specific_date=None, daily_or_weekly=None):
    """

    :param name: str
    :param specific_date: str, date in format (for example) "Thu 9/21"
    :param daily_or_weekly: str, either "daily" or "weekly"
    :return:
    """
    days = _parse_time(specific_date=specific_date, daily_or_weekly=daily_or_weekly)

    if not days:
        error_msg = 'Error occurred when getting the ' + daily_or_weekly + ' schedule'
        if specific_date:
            error_msg += ' for ' + specific_date
        error_msg += '.'

        raise DateNotFoundError(error_msg)

    name_list = _parse_name_to_list(name)

    # Populate the dict with meetings
    meeting_dict = db.add_all_meetings_to_view(name_list=name_list, days=days)

    return meeting_dict


def _parse_name_to_list(name):
    """

    :param name: str
    :return:
    """
    # Get the correct list of names
    selected_name = name.lower()
    if selected_name == 'everyone':
        name_list = dr.all_names
    elif selected_name == 'associates only':
        name_list = dr.associate_name_list
    elif selected_name == 'companies only':
        name_list = dr.company_name_list
    else:
        name_list = [selected_name]

    return name_list


def _parse_time(specific_date, daily_or_weekly):
    """

    :param specific_date: str, date in format (for example) "Thu 9/21"
    :param daily_or_weekly: str, either "daily" or "weekly"
    :return:
    """
    # Check base case
    if not specific_date and not daily_or_weekly:
        return None

    # Make sure that specific_days is a list of strings
    if specific_date:
        if not isinstance(specific_date, list):
            specific_date = [specific_date]

    if daily_or_weekly == 'daily':
        # Determine which day to send for
        if specific_date:
            # Format the data
            formatted_date = utils.format_day_picked(specific_date)
            specific_day = [formatted_date]
        else:
            specific_day = utils.get_next_day()

        # Pick out the appropriate sheet names from the list
        days = [x for x in vrs.sheet_options if specific_day in x]
    elif daily_or_weekly == 'weekly':
        if specific_date:
            # Format the data
            specific_week = utils.format_week_picked(specific_date)
            days = vrs.weeks.get(specific_week)
        else:
            days = utils.get_next_week()

        # TODO: make sure that the days of the week are some of the page options
    else:
        return None

    return days


# if create_calendar_events:
#     for name, event_list in meeting_dict.items():
#         try:
#             gcal_scheduler.add_cal_events(event_list)
#         except Exception:
#             traceback.print_exc()
#             continue


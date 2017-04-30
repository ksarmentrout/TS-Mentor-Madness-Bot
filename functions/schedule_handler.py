import traceback
from collections import defaultdict

import email_sender
import gcal_scheduler
from meeting import DividerMeeting
from database import db_interface as db
from functions.utilities import utils as utils
from functions.utilities import variables as vrs
from functions.utilities import directories as dr


def get_meeting_views(name, specific_date=None, daily_or_weekly=None):
    """
    Returns a dictionary for meetings, where keys are names
    and values are meeting lists.
    This is for displaying the meetings on the /view_schedule page
    :param name:
    :param specific_date:
    :param daily_or_weekly:
    :return:
    """
    # Add all the meetings
    meeting_dict = main_setup(
        name=name,
        specific_date=specific_date,
        daily_or_weekly=daily_or_weekly
    )

    return meeting_dict


def email_meetings(name, specific_date=None, daily_or_weekly=None):
    meeting_dict = main_setup(
        name=name,
        specific_date=specific_date,
        daily_or_weekly=daily_or_weekly
    )

    try:
        email_sender.send_daily_mail(meeting_dict)
    except Exception:
        traceback.print_exc()
    return None


def main_setup(name, specific_date=None, daily_or_weekly=None):
    days = parse_time(specific_date=specific_date, daily_or_weekly=daily_or_weekly)

    if not days:
        return None

    name_list = parse_name_to_list(name)

    # Populate the dict with meetings
    meeting_dict = db.add_all_meetings_to_view(name_list=name_list, days=days)

    return meeting_dict


def parse_name_to_list(name):
    """

    :param name:
    :return:
    """
    # Get the right list of names
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


def parse_time(specific_date, daily_or_weekly):
    """

    :param specific_date:
    :param daily_or_weekly:
    :return:
    """
    # Check base case
    if specific_date is None and daily_or_weekly is None:
        return None

    # Make sure that specific_days is a list
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
    else:
        raise KeyError("Unrecognized value '" + daily_or_weekly + "' in time selection.")

    return days


# if create_calendar_events:
#     for name, event_list in meeting_dict.items():
#         try:
#             gcal_scheduler.add_cal_events(event_list)
#         except Exception:
#             traceback.print_exc()
#             continue



if __name__ == '__main__':
    main_setup(send_emails=True, specific_day='Mon 3/6')
    # main()

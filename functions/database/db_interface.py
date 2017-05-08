from collections import defaultdict

import pandas as pd

# Local imports
from database import Connection
from database import db_logging as db
from utilities import directories as dr
from utilities import utils
from meeting import DividerMeeting


def add_to_db(mtg):
    """

    :param mtg: Meeting object or list of Meeting objects
    :return:
    """
    # Make the Meeting object part of a list if it isn't already
    if not isinstance(mtg, list):
        mtg = [mtg]

    return db.log_info(meeting_info_list=mtg)


def get_all_meetings():
    return db.get_all_meetings()


def meeting_search(criteria_dict):
    return db.meeting_search(criteria_dict)


def get_saved_meeting(mtg):
    """

    :param mtg: Meeting object
    :return:
    """
    return db.get_saved_meeting(mtg)


def get_all_daily_schedules(name, name_type, day):
    """

    :param name: company or associate name to match in database
    :param name_type: str, either 'company' or 'associate'
    :param day: str, day to match in the database
    :return:
    """
    criteria_dict = {
        name_type: name,
        'day': day
    }

    meeting_list = db.meeting_search(criteria_dict)

    if not meeting_list:
        return []

    # Sort the daily schedules by time
    meeting_list.sort(key=lambda x: x.start_time)

    return meeting_list


def add_all_meetings_to_view(name_list, days):
    """

    :param name_list:
    :param days:
    :return:
    """
    # Initialize dictionary for meetings
    meeting_dict = defaultdict(list)

    for name in name_list:
        name_type = utils.get_name_type(name)

        # Get proper name
        proper_name = utils.get_proper_name(name)

        for day in days:
            # Create a divider with only the day filled in
            divider = DividerMeeting(day)
            meeting_dict[proper_name].append(divider)

            # Add all meetings for that day
            meeting_list = get_all_daily_schedules(name, name_type, day)

            # Add meetings to the list for a given name
            meeting_dict[proper_name].extend(meeting_list)

    return meeting_dict


def delete_meeting(info):
    """

    :param info: Meeting object
    :return:
    """
    return db.delete_meeting(info)


def process_changes(meetings):
    if not meetings:
        return
    if not isinstance(meetings, list):
        meetings = [meetings]

    return db.process_changes(meetings)


def add_meeting_cal_event_ids(meeting_dict):
    try:
        db.add_meeting_cal_event_ids(meeting_dict)
        return True
    except:
        return False


def get_db_as_df():
    """
    Returns the entire database as a Pandas DataFrame.
    :return:
    """
    df = pd.read_sql_table('meetings', Connection())
    return df

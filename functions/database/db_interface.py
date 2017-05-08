from collections import defaultdict

import pandas as pd

# Local imports
from database import Connection
from database import db_logging as db
from utilities import directories as dr
from utilities import utils
from meeting import DividerMeeting


def add_to_db(mtg, session=None):
    """
    Wrapper to add a Meeting to the database.

    :param mtg: Meeting object or list of Meeting objects
    :param session: instance of SQLAlchemy Session object for testing
    :return:
    """
    # Make the Meeting object part of a list if it isn't already
    if not isinstance(mtg, list):
        mtg = [mtg]

    return db.log_info(meeting_info_list=mtg, session=session)


def get_all_meetings(session=None):
    """
    Get all meetings from the database as a list of Meeting objects.

    :param session: instance of SQLAlchemy Session object for testing
    :return:
    """
    return db.get_all_meetings(session=session)


def meeting_search(criteria_dict, session=None):
    """
    Simple wrapper for filtering by meeting attributes.

    :param criteria_dict: dictionary of parameters to search for meetings
    :param session: instance of SQLAlchemy Session object for testing
    :return:
    """
    return db.meeting_search(criteria_dict, session=session)


def get_saved_meeting(mtg, session=None):
    """

    :param mtg: Meeting object
    :param session: instance of SQLAlchemy Session object for testing
    :return:
    """
    return db.get_saved_meeting(mtg, session=session)


def get_all_daily_schedules(name, name_type, day, session=None):
    """

    :param name: company or associate name to match in database
    :param name_type: str, either 'company' or 'associate'
    :param day: str, day to match in the database
    :param session: instance of SQLAlchemy Session object for testing
    :return:
    """
    criteria_dict = {
        name_type: name,
        'day': day
    }

    meeting_list = db.meeting_search(criteria_dict, session=session)

    if not meeting_list:
        return []

    # Sort the daily schedules by time
    meeting_list.sort(key=lambda x: x.start_time)

    return meeting_list


def add_all_meetings_to_view(name_list, days, session=None):
    """

    :param name_list:
    :param days:
    :param session: instance of SQLAlchemy Session object for testing
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
            meeting_list = get_all_daily_schedules(name, name_type, day, session=session)

            # Add meetings to the list for a given name
            meeting_dict[proper_name].extend(meeting_list)

    return meeting_dict


def delete_meeting(info, session=None):
    """

    :param info: Meeting object
    :param session: instance of SQLAlchemy Session object for testing
    :return:
    """
    return db.delete_meeting(info, session=session)


def process_changes(meetings, session=None):
    """

    :param meetings:
    :param session:
    :return:
    """
    if not meetings:
        return
    if not isinstance(meetings, list):
        meetings = [meetings]

    return db.process_changes(meetings, session=session)


def add_meeting_cal_event_ids(meeting_dict, session=None):
    """

    :param meeting_dict:
    :param session:
    :return:
    """
    try:
        db.add_meeting_cal_event_ids(meeting_dict, session=session)
        return True
    except:
        return False


def get_db_as_df(testing=False):
    """
    Returns the entire database as a Pandas DataFrame.

    :param testing: bool
    :return:
    """
    if testing:
        table_name = 'test_db'
    else:
        table_name = 'meetings'

    df = pd.read_sql_table(table_name, Connection())
    return df

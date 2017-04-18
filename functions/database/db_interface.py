import pandas as pd

# Local imports
from database import Connection
from database import db_logging as db


def add_to_db(mtg):
    """

    :param mtg: Meeting object or list of Meeting objects
    :return:
    """
    db.log_info(meeting_info=mtg)


def get_all_meetings():
    return db.get_all_meetings()


def meeting_search(criteria_dict):
    return db.meeting_search(criteria_dict)


def delete_meeting(info):
    return db.delete_meeting(info)


def process_changes(meetings):
    if not meetings:
        return
    if not isinstance(meetings, list):
        meetings = [meetings]

    return db.process_changes(meetings)


def update_saved_meeting(old_meeting, new_meeting):
    return db.update_meeting(old_meeting, new_meeting)


def get_db_as_df():
    """
    Returns the entire database as a Pandas DataFrame.
    :return:
    """
    df = pd.read_sql_table('meetings', Connection())
    return df

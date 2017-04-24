import pandas as pd

# Local imports
from database import Connection
from database import db_logging as db
from utilities import directories as dr
from utilities import utils
from meeting import Meeting


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


def get_saved_meeting(info):
    """

    :param info: Meeting object
    :return:
    """
    return db.get_saved_meeting(info)


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


def _add_all_meetings_to_view(meeting_dict, name_list, days):
    """

    :param meeting_dict:
    :param name:
    :param name_type:
    :param proper_name:
    :param day:
    :return:
    """
    for name in name_list:
        name_type = utils.get_name_type(name)

        # Get proper name
        proper_name = utils.get_proper_name(name)

        # Initialize meeting list for name
        meeting_dict[proper_name] = []

        for day in days:
            # Create a divider with only the day filled in
            divider = Meeting()
            divider.day = day
            meeting_dict[proper_name].append(divider)

            # Add all meetings for that day
            meeting_list = get_all_daily_schedules(name, name_type, day)
            for x in meeting_list:
                if x.associate:
                    x.associate = utils.get_proper_name(x.associate)

            meeting_dict[proper_name].extend(meeting_list)

    return meeting_dict


def get_meeting_views(page_dict):
    """
    Returns a dictionary for meetings, where keys are names
    and values are meeting lists.
    This is for displaying the meetings on the /view_schedule page
    :param page_dict:
    :return:
    """

    print('entered get_meeting_views\n')
    # Get the right list of names
    selected_name = page_dict['name'].lower()
    if selected_name == 'everyone':
        name_list = dr.all_names
    elif selected_name == 'associates only':
        name_list = dr.associate_name_list
    elif selected_name == 'companies only':
        name_list = dr.company_name_list
    else:
        name_list = [selected_name]

    # Initialize empty meeting dict
    meeting_dict = {}

    # Make sure that days is a list of strings
    days = page_dict['date']
    if not isinstance(days, list):
        days = [days]

    if page_dict['daily_or_weekly'] == 'daily':
        print('entered daily\n')
    else:
        print('entered weekly\n')

    # Add all the meetings
    meeting_dict = _add_all_meetings_to_view(meeting_dict=meeting_dict, name_list=name_list, days=days)

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

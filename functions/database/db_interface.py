import math
import datetime

# Local imports
from database.db_errors import *
import database.db_tables as tables
from database import Session
from meeting import Meeting
from database import db_logging as db


def add_to_db(mtg):
    """

    :param info:
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


def update_db_entry(info):
    new_info = _make_paper_info(info)

    # Get the saved information that exists for a given entry
    saved_info = get_saved_entry_obj(new_info)

    main_paper_id = saved_info.main_paper_id

    # Turn the new information into a combined dict
    new_full_dict = new_info.__dict__.copy()
    new_full_dict.update(new_info.entry.__dict__)
    if new_full_dict.get('authors') is not None:
        new_full_dict['authors'] = [author.__dict__ for author in new_full_dict['authors']]

    # Turn saved information into a combined dict
    saved_full_dict = saved_info.__dict__.copy()
    saved_full_dict.update(saved_info.entry.__dict__)
    if saved_full_dict.get('authors') is not None:
        saved_full_dict['authors'] = [author.__dict__ for author in saved_full_dict['authors']]

    updating_fields = []
    updating_values = []

    # Determine which fields have changed and need to be updated
    for field in comparison_fields:
        saved = saved_full_dict.get(field)
        new = new_full_dict.get(field)
        if saved == new:
            continue
        else:
            updating_fields.append(field)
            if saved is not None:
                updating_values.append(saved)
            else:
                updating_values.append(new)

    # Make the updating requests
    update_general_fields(new_full_dict.get('title'), updating_field=updating_fields,
                             updating_value=updating_values, filter_by_title=True)


def check_multiple_constraints(params):
    # Params is a dict

    # first_key, first_value = params.popitem()
    # query_results = main_paper_search_wrapper(first_key, first_value)
    query_results = _get_all_meeting_objs()

    for key, value in params.items():
        temp = []
        for result in query_results:
            search_value = getattr(result, key, '')
            if search_value is None:
                continue
            else:
                if value.lower() in search_value.lower():
                    temp.append(result)
        query_results = temp
        # query_results = [result for result in query_results if value.lower() in str(getattr(result, key, '')).lower()]
        if len(query_results) == 0:
            return None

    return query_results


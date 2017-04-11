import math

# Local imports
from database import db_logging as db


def add_to_db(info):
    paper_info = _make_paper_info(info)
    db.log_info(paper_info=paper_info)


def update_db_entry(info):
    new_info = _make_paper_info(info)

    # Get the saved information that exists for a given entry
    saved_info = db.get_saved_entry_obj(new_info)

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
    db.update_general_fields(new_full_dict.get('title'), updating_field=updating_fields,
                             updating_value=updating_values, filter_by_title=True)


def check_multiple_constraints(params):
    # Params is a dict

    # first_key, first_value = params.popitem()
    # query_results = db.main_paper_search_wrapper(first_key, first_value)
    query_results = db.get_all_meetings()

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

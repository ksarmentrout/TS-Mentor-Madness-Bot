import traceback
from collections import defaultdict

import email_sender
import gcal_scheduler
from meeting import DividerMeeting
from database import db_interface as db
from functions.utilities import utils as utils
from functions.utilities import variables as vrs
from functions.utilities import directories as dr


def get_meeting_views(name, date):
    """
    Returns a dictionary for meetings, where keys are names
    and values are meeting lists.
    This is for displaying the meetings on the /view_schedule page
    :param name:
    :param date:
    :return:
    """

    print('entered get_meeting_views\n')
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

    # Initialize empty meeting dict
    meeting_dict = {}

    # Make sure that days is a list of strings
    days = date
    if not isinstance(days, list):
        days = [days]

    # Add all the meetings
    meeting_dict = db.add_all_meetings_to_view(meeting_dict=meeting_dict, name_list=name_list, days=days)

    return meeting_dict


def email_meetings():
    pass


def main(name=None, specific_day=None, send_emails=True):
    # Set variables
    sheet_options = vrs.sheet_options

    # Determine which day to send for
    if specific_day:
        match_day = specific_day
    else:
        match_day = utils.get_next_day()

    # Pick out the appropriate sheet names from the list
    sheet_names = [x for x in sheet_options if match_day in x]

    if not sheet_names:
        return None

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

    # Populate the dict with meetings
    meeting_dict = make_meeting_dict(sheet_names, name_list)

    if send_emails:
        try:
            email_sender.send_daily_mail(meeting_dict)
        except Exception:
            traceback.print_exc()
        return None
    else:
        return meeting_dict


def make_meeting_dict(sheet_names, name_list):
    """

    :param sheet_names:
    :param name_list:
    :return:
    """
    # Initialize dictionary of names, where
    # key = name, value = list of Meeting objs
    name_dict = defaultdict(list)

    for day in sheet_names:
        # Add a spacer meeting to separate days
        spacer_mtg = DividerMeeting(day)

        # Iterate through names
        for name in name_list:
            # Add the heading for the day
            name_dict[name].append(spacer_mtg)

            # Determine if the name is associate, company, or mentor
            if name in dr.associate_name_list:
                role = 'associate'
            elif name in dr.company_name_list:
                role = 'company'
            else:
                role = 'mentor'

            meetings = db.meeting_search(
                {
                    'day': day,
                    role: name
                }
            )
            name_dict[name].extend(meetings)

        print('Got info for ' + day)

    return name_dict


# if create_calendar_events:
#     for name, event_list in meeting_dict.items():
#         try:
#             gcal_scheduler.add_cal_events(event_list)
#         except Exception:
#             traceback.print_exc()
#             continue



if __name__ == '__main__':
    main(create_calendar_events=False, send_emails=True, specific_day='Mon 3/6')
    # main()

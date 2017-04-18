import traceback

import email_sender
import gcal_scheduler
from meeting import Meeting
from database import db_interface as db
from functions.utilities import utils as utils
from functions.utilities import variables as vrs
from functions.utilities import directories as dr


def main(team=None, specific_day=None, send_emails=True, create_calendar_events=False):
    # Set variables
    sheet_options = vrs.sheet_options

    # Determine which day to send for
    match_day = utils.get_next_day()

    if specific_day:
        match_day = specific_day

    # Pick out the appropriate sheet names from the list
    sheet_names = [x for x in sheet_options if match_day in x]

    if team is None:
        name_dict = dr.empty_name_dict
    else:
        name_dict = {}
        if isinstance(team, list):
            for t in team:
                name_dict[t] = []
        else:
            name_dict[team] = []

    for day in sheet_names:
        # Add a spacer meeting to separate days
        spacer_mtg = Meeting()
        spacer_mtg.day = day

        for key, val in name_dict.items():
            name_dict[key].append(spacer_mtg)

        # Iterate through names
        for name in name_dict:
            # Determine if the name is an associate or company
            if name in dr.associate_name_list:
                role = 'associate'
            else:
                role = 'company'

            meetings = db.meeting_search(
                {
                    'day': day,
                    role: name
                }
            )
            name_dict[name].extend(meetings)

        print('Got info for ' + day)

    if create_calendar_events:
        for name, event_list in name_dict.items():
            try:
                gcal_scheduler.add_cal_events(event_list)
            except Exception:
                traceback.print_exc()
                continue

    if send_emails:
        try:
            email_sender.send_daily_mail(name_dict)
        except Exception:
            traceback.print_exc()
        return None
    else:
        return name_dict


if __name__ == '__main__':
    main(create_calendar_events=False, send_emails=True, specific_day='Mon 3/6')
    # main()

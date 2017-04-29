import email_sender
from meeting import DividerMeeting
from database import db_interface as db
from functions.utilities import utils
from functions.utilities import directories as dr
from functions.utilities import variables as vrs


def main(specific_week=None, send_emails=True):
    # Set variables
    name_dict = dr.empty_name_dict

    # Determine which week to send for
    if specific_week:
        sheet_names = vrs.weeks.get(specific_week)
    else:
        sheet_names = utils.get_next_week()

    if not sheet_names:
        return None

    for day in sheet_names:
        # Add a spacer meeting to separate days
        spacer_mtg = DividerMeeting(day)

        for key, val in name_dict.items():
            name_dict[key].append(spacer_mtg)

        # Iterate through names
        for name in name_dict:
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

    if send_emails:
        email_sender.send_weekly_mail(name_dict)


if __name__ == '__main__':
    main()

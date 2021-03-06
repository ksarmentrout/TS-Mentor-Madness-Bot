import csv
import smtplib
from email.mime.text import MIMEText

from functions.utilities import variables as vrs
from functions.utilities import utils
from functions.utilities import directories as dr
from utilities import email_templates
from database import db_interface as db


def send_added_msgs(msg_dict, server):
    """

    :param msg_dict: dictionary where keys: names and values: lists of Meeting objects
    :param server: instance of SMTP server
    :return:
    """
    for name, meeting_list in msg_dict.items():
        # clean_name = utils.process_name(name)

        # Group by day:
        day_list = [x.day for x in meeting_list]
        unique_days = set(day_list)

        name_type = ''
        first_meeting = meeting_list[0]
        if first_meeting.associate == name:
            name_type = 'associate'
        elif first_meeting.company == name:
            name_type = 'company'

        for day in unique_days:
            daily_meetings = [x for x in meeting_list if x.day == day]

            # Get full schedule for the day for that team or associate
            full_schedule = db.get_all_daily_schedules(name=name, name_type=name_type, day=day)

            if name == 'not_found':
                address_name = name
            else:
                address_name = dr.names_to_proper_names[name]

            # Load email template and populate with personalized info
            msg = email_templates.added_meeting_msg

            added_meeting_list = _bulk_event_formatter(daily_meetings)
            msg.replace('[ADDED MEETING LIST]', added_meeting_list)
            msg.replace(['[ADDRESS NAME]'], address_name)
            msg.replace(['[DAY]'], day)

            event_list = _bulk_event_formatter(full_schedule[name])
            if not event_list:
                msg.replace('[FULL MEETING LIST]', '\n\nNo meetings!')
            else:
                msg.replace('[FULL MEETING LIST]', ''.join(event_list))

            to_addresses = dr.update_email_list[name]

            # Make the addresses into a list
            if not isinstance(to_addresses, list):
                to_addresses = [to_addresses]

            # Get the start times for added meetings of a given day
            meeting_start_times = [x.start_time for x in daily_meetings]
            if len(meeting_start_times) > 1:
                start_times = ', '.join(meeting_start_times)
            else:
                start_times = meeting_start_times[0]

            # Send an email to each person
            for addr in to_addresses:
                message = MIMEText(msg)
                message['From'] = 'mentor.madness.bot@gmail.com'
                message['To'] = addr
                message['Subject'] = 'New mentor meeting at ' + start_times + ' on '+ day

                server.send_message(message)
                print('Sent added email - ' + address_name + ' for ' + day)


def send_deleted_msgs(mtg_dict, server):
    """

    :param mtg_dict: dictionary where keys: names and values: lists of Meeting objects
    :param server: instance of SMTP server
    :return:
    """
    for name, meeting_list in mtg_dict.items():
        # Group by day:
        day_list = [x.day for x in meeting_list]
        unique_days = set(day_list)

        # Determine who the name corresponds to
        name_type = ''
        first_meeting = meeting_list[0]
        if first_meeting.associate == name:
            name_type = 'associate'
        elif first_meeting.company == name:
            name_type = 'company'

        for day in unique_days:
            daily_meetings = [x for x in meeting_list if x.day == day]

            # Get full schedule for the day for that team or associate
            full_schedule = db.get_all_daily_schedules(name=name, name_type=name_type, day=day)

            if name == 'not_found':
                address_name = name
            else:
                address_name = dr.names_to_proper_names[name]

            # Get email template
            msg = email_templates.deleted_meeting_msg

            # Format the meetings and insert them into the email template
            deleted_meeting_list = _bulk_event_formatter(daily_meetings)
            msg.replace('[DELETED MEETING LIST]', deleted_meeting_list)
            msg.replace(['[ADDRESS NAME]'], address_name)
            msg.replace(['[DAY]'], day)

            # Format the full schedule and insert that as well
            event_list = _bulk_event_formatter(full_schedule[name])
            if not event_list:
                msg.replace('[FULL MEETING LIST]', '\n\nNo meetings!')
            else:
                msg.replace('[FULL MEETING LIST]', ''.join(event_list))

            to_addresses = dr.update_email_list[name]

            if not isinstance(to_addresses, list):
                to_addresses = [to_addresses]

            # Get the start times for added meetings of a given day
            meeting_start_times = [x.start_time for x in daily_meetings]
            if len(meeting_start_times) > 1:
                start_times = ', '.join(meeting_start_times)
            else:
                start_times = meeting_start_times[0]

            for addr in to_addresses:
                message = MIMEText(msg)
                message['From'] = 'mentor.madness.bot@gmail.com'
                message['To'] = addr
                message['Subject'] = 'Cancelled mentor meeting at ' + start_times + ' on '+ day

                server.send_message(message)
                print('Sent deleted email - ' + address_name + ' for ' + day)


def send_update_mail(added_mtg_dict, deleted_mtg_dict):
    """

    :param added_mtg_dict: dict where keys: names w/ added meetings and values: lists of Meeting objects
    :param deleted_mtg_dict: dict where keys: names w/ deleted meetings and values: lists of Meeting objects
    :return:
    """
    server = _email_login()

    # Send mail
    send_added_msgs(added_mtg_dict, server)
    send_deleted_msgs(deleted_mtg_dict, server)

    # Close connection
    server.quit()


def send_daily_mail(mtg_dict):
    """

    :param mtg_dict:
    :return:
    """
    server = _email_login()

    for key, events in mtg_dict.items():
        msg = email_templates.daily_mail_msg

        event_list = _bulk_event_formatter(events)
        if not event_list:
            msg.replace('[FULL MEETING LIST]', '\n\nNo meetings!')
        else:
            msg.replace('[FULL MEETING LIST]', ''.join(event_list))

        to_addresses = dr.daily_email_list[key]

        if isinstance(to_addresses, list):
            for addr in to_addresses:
                message = MIMEText(msg)
                message['From'] = 'mentor.madness.bot@gmail.com'
                message['To'] = addr
                message['Subject'] = 'Mentor meeting summary for tomorrow'

                server.send_message(message)
                print('Sent daily email to ' + key)
        else:
            message = MIMEText(msg)
            message['From'] = 'mentor.madness.bot@gmail.com'
            message['To'] = to_addresses
            message['Subject'] = 'Mentor meeting summary for tomorrow'

            server.send_message(message)
            print('Sent daily email to ' + key)

    server.quit()


def send_weekly_mail(mtg_dict):
    """

    :param mtg_dict:
    :return:
    """
    server = _email_login()

    for key, events in mtg_dict.items():
        msg = 'Hello ' + dr.names_to_proper_names[key] + ',\n\n' + \
              'Here are your scheduled meetings for this week:\n\n'

        event_list = _bulk_event_formatter(events)
        if not event_list:
            msg += 'No meetings!'
        else:
            msg += ''.join(event_list)

        msg += '\n\nThis represents the first draft for the week. Please check the main schedule if this is in error.\n\n' + \
              '- Scheduling Bot'

        to_addresses = dr.daily_email_list[key]

        if isinstance(to_addresses, list):
            for addr in to_addresses:
                message = MIMEText(msg)
                message['From'] = 'mentor.madness.bot@gmail.com'
                message['To'] = addr
                message['Subject'] = 'Mentor meeting summary for next week'

                server.send_message(message)
                print('Sent weekly email to ' + key)
        else:
            message = MIMEText(msg)
            message['From'] = 'mentor.madness.bot@gmail.com'
            message['To'] = to_addresses
            message['Subject'] = 'Mentor meeting summary for next week'

            server.send_message(message)
            print('Sent weekly email to ' + key)

    server.quit()


def make_daily_mentor_schedules(mentor_dict):
    """
    Generates

    :param mentor_dict:
    :return:
    """
    for key, events in mentor_dict.items():
        day = events[0].get('day')

        msg = email_templates.mentor_reminder_msg
        msg.replace('[KEY]', key)
        msg.replace('[DAY]', day)

        event_list = _bulk_event_formatter(events, for_mentors=True)
        if not event_list:
            full_meeting_list = 'No meetings!'
        else:
            full_meeting_list = ''.join(event_list)

        msg.replace('[FULL MEETING LIST]', full_meeting_list)

        # Save message to a .txt file
        dirname = day.replace(' ', '_').replace('/', '_')
        txt_name = key.replace(' ', '_').strip() + '.txt'
        filename = vrs.LOCAL_PATH + '/mentor_schedules/' + dirname + '/' + txt_name
        with open(filename, 'w') as file:
            file.write(msg)


def make_mentor_packet_schedules(mentor_dict):
    """


    :param mentor_dict:
    :return:
    """
    for key, events in mentor_dict.items():
        day = events[0].get('day')

        msg = '<h1>' + key + '</h1><br/><br/>' + \
              '<h2>Schedule - ' + day + '</h2><br/><br/>'

        event_list = _bulk_event_formatter(events, for_mentors=True)
        if not event_list:
            msg += 'No meetings!'
        else:
            msg += '<br/><br/>'.join(event_list)

        # Save message to a .html file
        dirname = day.replace(' ', '_').replace('/', '_')
        txt_name = key.replace(' ', '_').strip() + '.html'
        filename = vrs.LOCAL_PATH + '/mentor_packet_schedules/' + dirname + '/' + txt_name
        with open(filename, 'w') as file:
            file.write(msg)


def _email_login():
    """
    Helper function to log in to the gmail account for the Mentor
    Madness Bot and return an instance of the authenticated server.

    :return: an instance of an SMTP server
    """
    # Get login credentials from stored file
    login_file = vrs.LOCAL_PATH +'mm_bot_gmail_login.txt'
    file = open(login_file, 'r')
    reader = csv.reader(file)
    row = next(reader)
    username = row[0]
    password = row[1]
    file.close()

    # Start email server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user=username, password=password)

    return server


def _bulk_event_formatter(event_list, for_mentors=False):
    """


    :param event_list: list of Meeting objects
    :param for_mentors: bool specifying if the meeting summary is for a mentor
    :return: list of formatted strings, each summarizing a meeting
    """
    # First check to see if the event dict list is made up only of headers.
    # In this case, there are no actual events, so return an empty list
    if not any(ed.get('start_time', False) for ed in event_list):
        return []

    event_list = []
    for ed in event_list:
        # Choose either mentor name or team name
        if for_mentors:
            room_subject = ed.get('company')
            if room_subject:
                room_subject = dr.names_to_proper_names[room_subject]
        else:
            room_subject = ed.get('mentor')

        if ed.get('start_time') is None:
            event_list.append('\n\n' + ed.get('day') + '\n')
        else:
            msg = '\n\t' + ed.get('start_time') + ' - ' + room_subject + \
                '\n\t' + 'Room ' + ed.get('room_num') + ' (' + ed.get('room_name') + ')\n'
            event_list.append(msg)

    return event_list

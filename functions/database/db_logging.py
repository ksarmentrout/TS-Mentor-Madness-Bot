import sqlalchemy as sql

from database.db_errors import *
import database.db_tables as tables
from database import Session

from meeting import Meeting
from utilities import utils
from utilities import directories as dr


def meeting_search(criteria_dict):
    # Simple wrapper for filtering by row entries
    session = Session()
    query_results = session.query(tables.Meetings).filter_by(**criteria_dict).all()
    result_objects = _create_meeting_list_from_saved(meeting_db_entries=query_results)
    _end(session)
    return result_objects


def get_all_meetings():
    # Returns entirety of Meetings table
    session = Session()
    results = session.query(tables.Meetings).all()
    result_objects = _create_meeting_list_from_saved(meeting_db_entries=results)
    _end(session)
    return result_objects


def get_saved_meeting(info):
    # Start a new Session
    session = Session()

    saved_meeting = _get_unique_meeting(info)
    meeting_list = _create_meeting_list_from_saved(saved_meeting)

    if meeting_list:
        meeting = meeting_list[0]
    else:
        meeting = None

    _end(session)
    return meeting


def log_info(meeting_info):
    # Start a new Session
    session = Session()

    # Create entry for main paper table
    if isinstance(meeting_info, list):
        for mtg in meeting_info:
            main_entry = _create_meeting_table_obj(mtg)

            # Add main entry to the table
            session.add(main_entry)

            # Get primary key for main entry
            # session.flush()
            # session.refresh(main_entry)

    else:
        main_entry = _create_meeting_table_obj(meeting_info)

        # Add main entry to the table
        session.add(main_entry)

        # Get primary key for main entry
        # session.flush()
        # session.refresh(main_entry)

    _end(session)


def process_changes(meetings):
    # Start a new Session
    session = Session()

    adding = dr.empty_name_dict
    deleting = dr.empty_name_dict

    for mtg in meetings:
        # Check if there was a meeting saved.
        saved_mtg = get_saved_meeting(mtg)

        # If there was not a saved meeting, append the meeting
        # to the company and associate lists
        if not saved_mtg:
            adding[mtg.get('company')].append(mtg)
            adding[mtg.get('associate')].append(mtg)

        # If there was a saved meeting, compare old with new
        else:
            saved_mtg = saved_mtg[0]
            for name in ['company', 'associate']:
                new_name = mtg.get(name)
                old_name = saved_mtg.get(name)
                if new_name != old_name:
                    if new_name and old_name:
                        # Someone was changed, assuming the names are different
                        if utils.process_name(new_name) != utils.process_name(old_name):
                            deleting[old_name].append(saved_mtg)
                            adding[new_name].append(mtg)
                        else:
                            continue
                    elif old_name:
                        # Someone was deleted
                        deleting[old_name].append(saved_mtg)
                    elif new_name:
                        # Someone was added
                        adding[new_name].append(mtg)

        update_meeting(old_meeting=saved_mtg, new_meeting=mtg, session=session, end_session=False)

    _end(session)

    email_target_dict = {
        'adding': adding,
        'deleting': deleting
    }

    return email_target_dict


def update_meeting(old_meeting, new_meeting, session=None, end_session=True):
    if session is None:
        session = Session()

    saved_mtg = _get_unique_meeting(old_meeting, session=session)
    saved_mtg.mentor = new_meeting.mentor
    saved_mtg.company = new_meeting.company
    saved_mtg.associate = new_meeting.associate

    session.flush()
    session.commit()

    if end_session:
        _end(session)


def add_meeting_cal_event_ids(meeting_dict):
    # if not isinstance(meetings, list):
    #     meetings = [meetings]

    session = Session()

    for name, meetings in meeting_dict.iteritems():
        for meeting in meetings:
            saved_meeting = _get_unique_meeting(meeting, session)
            saved_meeting.company_cal_event_id = meeting.company_cal_event_id
            saved_meeting.associate_cal_event_id = meeting.associate_cal_event_id

    session.flush()
    session.commit()
    _end(session)


def delete_meeting(info):
    """
    """
    session = Session()

    if not isinstance(info, list):
        info = [info]

    for item in info:
        try:
            meeting = _get_unique_meeting(item, session=session)
        except MeetingNotFoundError:
            return True

        session.delete(meeting)

    _end(session)

    return True


def _update_objects(entries, updating_field, updating_value):
    """
    Handles all attribute setting to update database session objects.

    Parameters
    ----------
    See 'update_entry_field'

    """
    # If there are multiple fields to be updated
    if isinstance(updating_field, list):
        # Check if there are unique values for each of the updating fields
        if isinstance(updating_value, list) and len(updating_field) == len(updating_value):
            tuples = zip(updating_field, updating_value)
            for tuple in tuples:
                for entry in entries:
                    setattr(entry, tuple[0], tuple[1])
        # Otherwise, multiple fields are being updates to one value (unlikely)
        else:
            for entry in entries:
                for field in updating_field:
                    setattr(entry, field, updating_value)
    # Otherwise, updating a single field with a single value
    else:
        for entry in entries:
            setattr(entry, updating_field, updating_value)

    return entries


def _create_meeting_table_obj(mtg):
    db_meeting_entry = tables.Meetings(
        day=mtg.get('day'),
        room_number=mtg.get('room_number'),
        room_name=mtg.get('room_name'),
        start_time=mtg.get('start_time'),
        end_time=mtg.get('end_time'),

        mentor=mtg.get('mentor'),
        company=mtg.get('company'),
        associate=mtg.get('associate')
    )
    return db_meeting_entry


def _create_meeting_list_from_saved(meeting_db_entries=None):
    """

    :param meeting_db_entries:
    :return: list of Meeting objects
    """
    # Create references list
    entries = []

    if meeting_db_entries is None:
        return entries

    # Formatting each reference entry
    for m in meeting_db_entries:
        if not isinstance(m, dict):
            m = m.__dict__

        meeting_obj = Meeting(m)
        entries.append(meeting_obj)

    return entries


def _get_unique_meeting(mtg, session=None):
    """

    :param mtg: Meeting object or dictionary
    :param session: instance of Session object
    :return: Meetings database object (NOT a Meeting object!)
    """
    if session is None:
        session = Session()

    if isinstance(mtg, Meeting):
        mtg = mtg.__dict__

    unique_dict = {k: mtg[k] for k in ['day', 'room_number', 'start_time']}
    filter_rule = sql.and_(
        tables.Meetings.day == unique_dict['day'],
        tables.Meetings.room_number == unique_dict['room_number'],
        tables.Meetings.start_time == unique_dict['start_time'],
    )

    meeting = session.query(tables.Meetings).filter(filter_rule).all()
    # if len(meeting) == 0:
    #     raise MeetingNotFoundError('No meeting matching the description ' + str(info) + ' found in database.')
    # elif len(meeting) > 1:
    #     raise DatabaseError('Multiple meetings match "unique" criteria. Problem with _get_unique_meeting()?')
    if len(meeting) != 1:
        return None
    else:
        meeting = meeting[0]

    # _end(session)

    return meeting


def _meeting_exists_in_db(info):
    try:
        _get_unique_meeting(info)
        return True
    except MeetingNotFoundError:
        return False


def _end(session):
    # Commit and close the session
    try:
        session.commit()

        # Call remove on the Session object, not the session object.
        # This is to deal with having scoped_session
        Session.remove()
    except:
        session.rollback()
        raise DatabaseError('Error encountered while committing to database. '
                            'Most recent information may not have been saved.')
    finally:
        session.close()

# Standard
import datetime

# Local imports
from database.db_errors import *
import database.db_tables as tables
from database import Session
from meeting import Meeting


def meeting_search(key, value):
    # Simple wrapper for filtering by one row entry
    session = Session()
    query_results = session.query(tables.Meetings).filter_by(**{key: value}).all()
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


def get_saved_info(doi):
    # Start a new Session
    session = Session()

    # Get papers with the requested DOI
    # This should only be 1
    main_results = session.query(tables.Meetings).filter(
        (tables.Meetings.doi == doi) | (tables.Meetings.doi == doi.lower())).all()
    if len(main_results) > 1:
        raise MultipleDoiError('Multiple papers with the same DOI found')
    elif len(main_results) == 0:
        return None

    main_paper = main_results[0]
    main_id = main_paper.id

    # Make into a Meeting object
    saved_paper_info = _create_meeting_list_from_saved(main_paper=main_paper)

    _end(session)
    return saved_paper_info


def log_info(meeting_info):
    # Start a new Session
    session = Session()

    # if doi is not None:
    #     doi = doi.lower()
    #
    #     # Check if the DOI is already in the main paper database
    #     existing_doi = session.query(tables.Meetings).filter_by(doi=doi).all()
    #     if len(existing_doi) > 0:
    #         return
    # elif title is not None:
    #     existing_title = session.query(tables.Meetings).filter_by(title=title).all()
    #     if len(existing_title) > 0:
    #         return

    # Create entry for main paper table
    main_entry = _create_meeting_table_obj(meeting_info)

    # Add main entry to the table
    session.add(main_entry)

    # Get primary key for main entry
    session.flush()
    session.refresh(main_entry)
    main_paper_id = main_entry.id

    _end(session)


def update_entry_field(identifying_value, updating_field, updating_value):
    """
    Updates a field or fields within the MainPaperInfo database table.

    Parameters
    ----------
    identifying_value : str
        Can be a paper title or DOI - used to identify which entries are being updated.
    updating_field : str or list
        The field(s) of the database table to be updated.
    updating_value : str or list
        The value(s) to populate the updating field(s).
    """
    session = Session()
    if filter_by_title:
        entries = session.query(tables.Meetings).filter_by(title=identifying_value).all()
    elif filter_by_doi:
        entries = session.query(tables.Meetings).filter_by(doi=identifying_value).all()
    else:
        _end(session)
        return

    entries = _update_objects(entries, updating_field=updating_field, updating_value=updating_value)
    _end(session)


def update_general_fields(identifying_value, updating_field, updating_value,
                          main_paper_id=None):
    """
    Updates a field or fields within the database.

    Parameters
    ----------
    See 'update_entry_field'

    """
    session = Session()

    if filter_by_title:
        # Case-insensitive search for matching with title
        main_entries = session.query(tables.Meetings).filter(
            tables.MainPaperInfo.title.ilike(identifying_value)).all()
    elif filter_by_doi:
        main_entries = session.query(tables.Meetings).filter(
            tables.MainPaperInfo.doi.ilike(identifying_value)).all()
    else:
        _end(session)
        return

    if len(main_entries) == 0:
        raise DatabaseError('No saved documents found.')

    if main_paper_id is None:
        main_paper_id = main_entries[0].id

    author_entries = session.query(tables.Authors).filter_by(main_paper_id=main_paper_id).all()

    zipped = zip(updating_field, updating_value)
    for field, value in zipped:
        # If the field is specific to a certain author, update the author objects
        if field in ['name', 'affiliations', 'email']:
            author_entries = _update_objects(author_entries, updating_field=field, updating_value=value)
            continue
        else:
            main_entries = _update_objects(main_entries, updating_field=field, updating_value=value)

    _end(session)


def get_saved_entry_obj(new_info):
    session = Session()

    if new_info.doi is not None:
        saved_obj = session.query(tables.MainPaperInfo).filter_by(doi=new_info.doi).all()
    elif new_info.entry.title is not None:
        saved_obj = session.query(tables.MainPaperInfo).filter_by(title=new_info.entry.title).all()
    else:
        raise KeyError('No title or DOI found within updating entry')

    if len(saved_obj) > 1:
        raise DatabaseError('Multiple entries with the same DOI or title were found.')
    elif len(saved_obj) == 0:
        raise DatabaseError('No saved paper with matching DOI or title was found.')

    saved_obj = saved_obj[0]
    main_id = saved_obj.id

    # Get author information
    authors = session.query(tables.Authors).filter_by(main_paper_id=main_id).all()

    # Get references for the main paper
    refs = session.query(tables.References).join(tables.RefMapping). \
        filter(tables.RefMapping.main_paper_id == main_id).all()

    # Make into a PaperInfo object
    saved_info = _create_paper_info_from_saved(main_paper=saved_obj, authors=authors, refs=refs)

    saved_info.fields = saved_obj.fields
    if authors is not None:
        saved_info.author_fields = authors[0].fields
    else:
        saved_info.author_fields = None

    saved_info.main_paper_id = main_id

    _end(session)
    return saved_info


def delete_info(doi=None, title=None):
    """
    Note that this will rarely be used and is mainly for debugging
        and manual database management reasons. Even if a user opts to
        delete a document from his/her Mendeley library, the information
        will not be deleted from the database in case it is to be
        retrieved again later.
    """
    session = Session()

    if doi is not None:
        matching_entries = session.query(tables.MainPaperInfo).filter_by(doi=doi).all()
    elif title is not None:
        matching_entries = session.query(tables.MainPaperInfo).filter_by(title=title).all()
    else:
        raise KeyError('No information given to delete_info.')

    # Extract the main IDs for the entry information
    ids = []
    for entry in matching_entries:
        ids.append(entry.id)
        session.delete(entry)

    # Delete all references, reference maps, and authors related to the IDs
    for id in ids:
        refs = session.query(tables.References).join(tables.RefMapping). \
            filter(tables.RefMapping.main_paper_id == id).all()
        for ref in refs:
            session.delete(ref)

        entry_map = session.query(tables.RefMapping).filter_by(main_paper_id=id).all()
        for map in entry_map:
            session.delete(map)

        authors = session.query(tables.Authors).filter_by(main_paper_id=id).all()
        for author in authors:
            session.delete(author)

    _end(session)


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


def _create_meeting_table_obj(m_dict):
    db_meeting_entry = tables.Meetings(
        day=m_dict.get('day'),
        room_number=m_dict.get('room_number'),
        room_name=m_dict.get('room_name'),
        start_time=m_dict.get('start_time'),
        end_time=m_dict.get('end_time'),

        mentor_name=m_dict.get('mentor_name'),
        company_name=m_dict.get('company_name'),
        associate_name=m_dict.get('associate_name')
    )
    return db_meeting_entry


def _fetch_id(session, table_name, doi=None, title=None):
    """
    For a given paper, it looks to see if it already exists in a table
    'table_name' and if so, returns the primary key of its entry in that table.

    Parameters
    ----------
    table_name : Base object (from db_tables.py)
        The table in the database that will be queried.
    doi : str
        Paper DOI
    title : str
        Paper title

    Returns
    -------
    primary_id : int
        Primary key of the entry corresponding to 'doi' and/or 'title' within
         'table_name'
    """

    if doi is not None:
        paper = session.query(table_name).filter((table_name.doi == doi) | (table_name.doi == doi.lower())).all()
        if len(paper) > 0:
            main_paper_id = paper[0].id
        else:
            main_paper_id = None
    elif title is not None:
        paper = session.query(table_name).filter_by(title=title).all()
        if len(paper) > 0:
            main_paper_id = paper[0].id
        else:
            main_paper_id = None
    else:
        raise LookupError('Cannot establish main paper to link with references.')

    return main_paper_id


def _create_meeting_list_from_saved(meeting_db_entries=None):
    """

    :param meeting_db_entries:
    :return:
    """
    # Create references list
    entries = []

    if meeting_db_entries is None:
        return entries

    # Formatting each reference entry
    for m in meeting_db_entries:
        if not isinstance(m, dict):
            m = m.__dict__

        meeting_obj = Meeting()
        for k, v in m.items():
            if k != 'timestamp':
                setattr(meeting_obj, k, v)
        entries.append(meeting_obj)

    return entries


def _end(session):
    # Commit and close the session
    try:
        session.commit()
    except:
        session.rollback()
        raise DatabaseError('Error encountered while committing to database. '
                            'Most recent information may not have been saved.')
    finally:
        session.close()

from database import db_interface as db
from utilities import utils
from utilities import directories as dr

'''
Types of stats that would be interesting:
    Meeting counts across companies and associates.
    Which mentors companies and associates met with.
    Total list of mentors.

    Buttons: "Get meeting counts," "Get mentor meeting info"

    Thoughts for another option: restrict time to "overall" vs. "up until present day" (so far)
'''


def get_stats(mentor=None, company=None, associate=None):
    df = db.get_db_as_df()

    df = df.drop(['start_time', 'end_time', 'room_number', 'room_name'], 1)

    stat_dict = {}

    # Filter by search criteria (e.g. {'associate': 'keaton'}) if provided
    # Check if none are present
    if not mentor and not company and not associate:
        # Get company meeting counts,
        pass

    # Check for only one
    elif mentor and not company and not associate:
        pass
    elif company and not associate and not mentor:
        df = df[df['company'] == company]
    elif associate and not mentor and not company:
        df = df[df['associate'] == associate]

    # Check if two of the three are present
    elif mentor and company and not associate:
        pass
    elif mentor and associate and not company:
        pass
    elif company and associate and not mentor:
        pass

    # All three are present!
    else:
        pass


    # Format the names
    df['company'] = df['company'].apply(utils.get_proper_name)
    df['associate'] = df['associate'].apply(utils.get_proper_name)

    # print(len(df))
    company_vals = df['company'].value_counts().to_frame()
    company_vals = company_vals.reindex(dr.company_proper_names)
    associate_vals = df['associate'].value_counts().to_frame()
    associate_vals = associate_vals.reindex(dr.associate_proper_names)

    # print(company_vals.to_html())

    return None


def get_mentor_list():
    df = db.get_db_as_df()
    mentor_list = df['mentor'].unique()
    print(len(mentor_list))
    return mentor_list


if __name__ == '__main__':
    get_stats()

# Third party imports
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Meetings(Base):
    __tablename__ = 'meetings'

    # id = sql.Column(sql.INTEGER, primary_key=True)

    day = sql.Column(sql.VARCHAR)
    room_number = sql.Column(sql.INTEGER)
    room_name = sql.Column(sql.VARCHAR)
    start_time = sql.Column(sql.VARCHAR)
    end_time = sql.Column(sql.VARCHAR)

    mentor_name = sql.Column(sql.VARCHAR)
    company_name = sql.Column(sql.VARCHAR)
    associate_name = sql.Column(sql.VARCHAR)

    timestamp = sql.Column(sql.TIMESTAMP)

    # Define composite primary key
    sql.PrimaryKeyConstraint(
        'day',
        'start_time',
        'room_number',
        name='id'
    )

    # This is used for comparisons with updated information.
    fields = [
        'day', 'room_number', 'room_name', 'start_time',
        'end_time', 'mentor_name', 'company_name',
        'associate_name'
    ]

    def __repr__(self):
        return u'' \
               'day: %s\n' % self.day + \
               'room_number: %s\n' % self.room_number + \
               'room_name: %s\n' % self.room_name + \
               'start_time: %s\n' % self.start_time + \
               'end_time %s\n' % self.end_time + \
               'mentor_name: %s\n' % self.mentor_name + \
               'company_name: %s\n' % self.company_name + \
               'associate_name: %s\n' % self.associate_name

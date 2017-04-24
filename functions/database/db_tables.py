# Third party imports
import sqlalchemy as sql
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Meetings(Base):
    __tablename__ = 'meetings'

    day = sql.Column(sql.VARCHAR, primary_key=True)
    room_number = sql.Column(sql.INTEGER, primary_key=True)
    room_name = sql.Column(sql.VARCHAR)
    start_time = sql.Column(sql.VARCHAR, primary_key=True)
    end_time = sql.Column(sql.VARCHAR)

    mentor = sql.Column(sql.VARCHAR)
    company = sql.Column(sql.VARCHAR)
    associate = sql.Column(sql.VARCHAR)

    associate_cal_event_id = sql.Column(sql.VARCHAR)
    company_cal_event_id = sql.Column(sql.VARCHAR)

    timestamp = sql.Column(sql.TIMESTAMP)

    # This is used for comparisons with updated information.
    fields = [
        'day', 'room_number', 'room_name', 'start_time',
        'end_time', 'mentor', 'company',
        'associate'
    ]

    def __repr__(self):
        return u'' \
               'day: %s\n' % self.day + \
               'room_number: %s\n' % self.room_number + \
               'room_name: %s\n' % self.room_name + \
               'start_time: %s\n' % self.start_time + \
               'end_time %s\n' % self.end_time + \
               'mentor: %s\n' % self.mentor + \
               'company: %s\n' % self.company + \
               'associate: %s\n' % self.associate

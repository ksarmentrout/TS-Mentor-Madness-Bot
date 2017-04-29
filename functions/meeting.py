from datetime import datetime, timedelta

from utilities import utils


class Meeting(object):
    def __init__(self, info_dict=None):
        self.day = None
        self.room_number = None
        self.room_name = None
        self.start_time = None
        self.end_time = None

        self.mentor = None
        self.company = None
        self.associate = None

        self.associate_cal_event_id = None
        self.company_cal_event_id = None

        self.is_populated = False
        self.is_divider = False

        if info_dict is not None:
            self.set_fields(info_dict)

        if self.mentor or self.company or self.associate:
            self.is_populated = True

    def set_fields(self, info_dict):
        # Populate end_time if only start_time was supplied.
        # Assume a default of a half hour meeting

        # TODO: finish this

        if self.start_time is not None and self.end_time is None:

            start_tm = datetime.strptime(self.start_time, '')

        for key, value in info_dict.items():
            self.__setattr__(key, value)

        # Process the names
        if self.company:
            self.company = utils.get_proper_name(self.company)
        if self.associate:
            self.associate = utils.get_proper_name(self.associate)

    def get(self, attr):
        return getattr(self, attr, None)

    @property
    def html_repr_array(self):
        s = []
        # Populate the string
        s.append(self.start_time + ' - ' + self.mentor)

        if self.room_name:
            location = 'Location: ' + self.room_name + ' (Room ' + str(self.room_number) + ')'
        else:
            location = 'Location: ' + 'Room ' + self.room_number

        s.append(location)

        return s

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


class DividerMeeting(Meeting):
    def __init__(self, day):
        super(DividerMeeting, self).__init__()

        self.is_populated = False
        self.is_divider = True
        self.day = day

    @property
    def html_repr_array(self):
        return [self.day]


class EmptyMeeting(Meeting):
    def __init__(self):
        super(EmptyMeeting, self).__init__()

        self.is_populated = False

    @property
    def html_repr_array(self):
        return ['No meetings!']

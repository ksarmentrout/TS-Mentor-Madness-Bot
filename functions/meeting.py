from datetime import datetime, timedelta


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

        if info_dict is not None:
            self.set_fields(info_dict)

    def set_fields(self, info_dict):
        # new_event_dict = {'time': timeslot, 'name': new_name, 'mentor': mentor_name,
        #                   'room_num': str(room_num), 'room_name': room_name, 'day': day}

        # Populate end_time if only start_time was supplied.
        # Assume a default of a half hour meeting
        if self.start_time is not None and self.end_time is None:



            start_tm = datetime.strptime(self.start_time, '')

        for key, value in info_dict.items():
            self.__setattr__(key, value)

    def get(self, attr):
        return getattr(self, attr, None)

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

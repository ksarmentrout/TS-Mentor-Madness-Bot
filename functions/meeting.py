from datetime import datetime, timedelta


class Meeting(object):
    def __init__(self, info_dict=None):
        self.day = None
        self.room_number = None
        self.room_name = None
        self.start_time = None
        self.end_time = None

        self.mentor_name = None
        self.company_name = None
        self.associate_name = None

        if info_dict is not None:
            self.set_fields(info_dict)

    def set_fields(self, info_dict):
        self.__setattr__(**info_dict)

        # Populate end_time if only start_time was supplied.
        # Assume a default of a half hour meeting
        if self.start_time is not None and self.end_time is None:



            start_tm = datetime.strptime(self.start_time, '')

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from functions import (
    email_sender,
    gcal_scheduler, generate_mentor_schedules, schedule_handler,
    sheets_scheduler, update_script
)
from functions.utilities import (
    directories, utils, variables
)


@pytest.fixture
def sheets_api():
    return utils.google_sheets_login()


@pytest.fixture
def cal_api():
    return utils.google_calendar_login()


class TestUtils:
    def test_google_login(self):
        utils.google_sheets_login()
        assert True

    def test_calendar_login(self):
        utils.google_calendar_login()
        assert True





class TestUserSuppliedInfo:
    def test_directories(self):
        pass

    def test_variables(self):
        pass




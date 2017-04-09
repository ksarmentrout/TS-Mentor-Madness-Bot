import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions import (
    csv_saving_script, daily_notice, email_sender,
    gcal_scheduler, generate_mentor_schedules, sheets_scheduler,
    update_script, weekly_notice
)
from functions.utilities import (
    directories, utils, variables
)

import pytest


class TestUtils:
    def test_google_login(self):
        utils.google_sheets_login()
        assert True


class TestUserSuppliedInfo:
    def test_directories(self):
        pass

    def test_variables(self):
        pass



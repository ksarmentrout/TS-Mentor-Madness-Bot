import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from functions import (
    csv_saving_script, schedule_handler, email_sender,
    gcal_scheduler, generate_mentor_schedules, sheets_scheduler,
    update_script, weekly_notice
)
from functions.utilities import (
    directories, utils, variables
)
from functions.database import (
    db_errors, db_interface, db_logging,
    db_tables, db_test
)


class TestUtils:
    def test_google_login(self):
        utils.google_sheets_login()
        assert True


class TestUserSuppliedInfo:
    def test_directories(self):
        pass

    def test_variables(self):
        pass


class TestDatabase:
    pass

# coding=utf-8
from __future__ import absolute_import, print_function

import os
import six
import sqlite3
from rigmanager.defaults import get_cfg_location


class ControlsDB(object):
    """Controls data base Python Context to open and close database connections a bit more easily."""

    def __init__(self):
        super(ControlsDB, self).__init__()
        self.connection = self.connect()
        self.cursor = self.connection.cursor()

    def connect(self):
        db_file = os.path.join(get_cfg_location(), "controls.db")
        connection = sqlite3.connect(db_file)
        connection.row_factory = (
            sqlite3.Row
        )  # sqlite will return type will be more like a dict
        return connection

    def __enter__(self):
        self.connection = self.connect()
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, type, value, traceback):
        if self.connection:
            self.connection.close()

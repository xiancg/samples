# coding=utf-8
from __future__ import absolute_import, print_function

import six
from rigmanager.orm import data


class AbstractEntity(object):
    def __init__(self, controlsdb=None):
        super(AbstractEntity, self).__init__()
        self._data = dict()
        self.controlsdb = controlsdb

    @classmethod
    def from_data(cls, controlsdb, db_data):
        this = cls()
        this.controlsdb = controlsdb
        for key in db_data.keys():
            this._data[key] = db_data[key]

        return this

    def save(self):
        entity_data = object.__getattribute__(self, "_data")
        values_str = data._format_update_values(self.controlsdb, "Control", entity_data)
        id_str = "{0}ID=:{0}ID".format(self.__class__.__name__.lower())
        query = "UPDATE {} SET {} WHERE {}".format(
            self.__class__.__name__, values_str, id_str
        )
        self.controlsdb.cursor.execute(query, entity_data)

    def __getattribute__(self, key):
        entity_data = object.__getattribute__(self, "_data")
        if key in entity_data.keys():
            return entity_data.get(key)
        return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        if key not in ["_data"]:
            self._data[key] = value
            return
        else:
            return super(AbstractEntity, self).__setattr__(key, value)

    def __repr__(self):
        pairs = list()
        for key, value in six.iteritems(self._data):
            pairs.append("{}: {}".format(key, value))
        output = ", ".join(pairs)

        return output

# coding=utf-8
from __future__ import absolute_import, print_function

import six
from sqlite3 import IntegrityError
from rigmanager.logger import logger
from rigmanager.orm import data
from rigmanager.orm.abstractentity import AbstractEntity
from rigmanager.orm.controlcolors import get_control_color
from rigmanager.orm.attributes import get_control_attributes
from rigmanager.orm.layers import get_layer
from rigmanager.orm.proximitygroups import (
    get_control_proximity_group,
    get_proximity_group_by_properties,
)
from rigmanager.orm.faceregions import (
    get_control_face_regions,
    get_face_region_by_properties,
)


__controls = dict()


class Control(AbstractEntity):
    def __init__(self):
        super(Control, self).__init__()
        self._color = None
        self._attributes = None
        self._layer = None
        self._face_regions = None
        self._proximity_group = None
        self._horizontal_match = None
        self._vertical_match = None

    @property
    def color(self):
        if not self._color:
            with self.controlsdb:
                self._color = get_control_color(self.controlsdb, self.controlcolorID)
        return self._color

    @property
    def attributes(self):
        if not self._attributes:
            with self.controlsdb:
                self._attributes = get_control_attributes(
                    self.controlsdb, self.controlID
                )
        return self._attributes

    @property
    def layer(self):
        if not self._layer:
            with self.controlsdb:
                self._layer = get_layer(self.controlsdb, self.layerID)
        return self._layer

    @property
    def face_regions(self):
        if not self._face_regions:
            with self.controlsdb:
                self._face_regions = get_control_face_regions(
                    self.controlsdb, self.controlID
                )
        return self._face_regions

    @property
    def proximity_group(self):
        if not self._proximity_group:
            with self.controlsdb:
                self._proximity_group = get_control_proximity_group(
                    self.controlsdb, self.controlID
                )
        return self._proximity_group

    @property
    def horizontal_match(self):
        if not self._horizontal_match:
            with self.controlsdb:
                self._horizontal_match = get_control_horizontal_match(
                    self.controlsdb, self.controlID
                )
        return self._horizontal_match

    @property
    def vertical_match(self):
        if not self._vertical_match:
            with self.controlsdb:
                self._vertical_match = get_control_vertical_match(
                    self.controlsdb, self.controlID
                )
        return self._vertical_match


def get_control(controlsdb, controlID):
    if not __controls.get(controlID):
        query = "SELECT * FROM Control WHERE controlID=:controlID"
        result = controlsdb.cursor.execute(query, {"controlID": controlID}).fetchone()
        __controls[controlID] = Control.from_data(controlsdb, result)
    return __controls.get(controlID)


def create_control(controlsdb, values):
    columns_str, placeholders_str, ordered_values = data._format_create_values(
        controlsdb, "Control", values
    )
    query = "INSERT INTO Control ({}) VALUES ({})".format(columns_str, placeholders_str)
    with controlsdb.connection:
        try:
            controlsdb.cursor.execute(query, ordered_values)
        except IntegrityError:
            logger.exception(
                "Control name {} is not unique.".format(values.get("name"))
            )
    return get_control(controlsdb, controlsdb.cursor.lastrowid)


def save_controls(controlsdb):
    for key, value in six.iteritems(__controls):
        value.save()


def delete_control(controlsdb, controlID):
    query = "DELETE from Control WHERE controlID=:controlID"
    with controlsdb.connection:
        controlsdb.cursor.execute(query, {"controlID": controlID})
    del __controls[controlID]


def get_control_by_name(controlsdb, control_name):
    for controlID, control_obj in six.iteritems(__controls):
        if control_obj.name == control_name:
            return control_obj
    query = "SELECT * FROM Control WHERE name=:control_name"
    result = controlsdb.cursor.execute(query, {"control_name": control_name}).fetchone()
    if result:
        __controls[result["controlID"]] = Control.from_data(controlsdb, result)
        return __controls.get(result["controlID"])
    return None


def get_controls_by_layer(controlsdb, layer_name):
    query = (
        "SELECT * FROM Control WHERE layerID="
        "(SELECT layerID FROM Layer WHERE name=:name)"
    )
    controlsdb.cursor.execute(query, {"name": layer_name.lower()})

    controls = list()
    for each in controlsdb.cursor:
        if not __controls.get(each["controlID"]):
            __controls[each["controlID"]] = Control.from_data(controlsdb, each)
        controls.append(__controls[each["controlID"]])
    if len(controls) >= 1:
        return controls
    return None


def get_controls_by_side(controlsdb, side):
    query = "SELECT * FROM Control WHERE side=:side"
    result = controlsdb.cursor.execute(query, {"side": side}).fetchall()
    controls = list()
    for each in result:
        if not __controls.get(each["controlID"]):
            __controls[each["controlID"]] = Control.from_data(controlsdb, each)
        controls.append(__controls[each["controlID"]])

    if len(controls) >= 1:
        return controls
    return None


def get_controls_by_side_and_layer(controlsdb, side, layerID):
    query = "SELECT * FROM Control WHERE side=:side AND layerID=:layerID"
    result = controlsdb.cursor.execute(
        query, {"side": side, "layerID": layerID}
    ).fetchall()
    controls = list()
    for each in result:
        if not __controls.get(each["controlID"]):
            __controls[each["controlID"]] = Control.from_data(controlsdb, each)
        controls.append(__controls[each["controlID"]])

    if len(controls) >= 1:
        return controls
    return None


def get_controls_by_color(controlsdb, color_name):
    query = (
        "SELECT * FROM Control WHERE controlcolorID IN "
        "(SELECT controlcolorID FROM ControlColor WHERE name=:name)"
    )
    controlsdb.cursor.execute(query, {"name": color_name.lower()})

    controls = list()
    for each in controlsdb.cursor:
        if not __controls.get(each["controlID"]):
            __controls[each["controlID"]] = Control.from_data(controlsdb, each)
        controls.append(__controls[each["controlID"]])

    if len(controls) >= 1:
        return controls
    return None


def get_controls_by_face_region(controlsdb, face_region_name, side, layerID=1):
    face_region = get_face_region_by_properties(
        controlsdb, face_region_name, side, layerID
    )
    if face_region:
        query = (
            "SELECT * FROM Control WHERE controlID IN "
            "(SELECT controlID FROM FaceRegionControl WHERE faceregionID=:faceregionID)"
        )
        result = controlsdb.cursor.execute(
            query, {"faceregionID": face_region.faceregionID}
        ).fetchall()

        controls = list()
        for each in result:
            if not __controls.get(each["controlID"]):
                __controls[each["controlID"]] = Control.from_data(controlsdb, each)
            controls.append(__controls[each["controlID"]])
        if len(controls) >= 1:
            return controls
    return None


def get_controls_by_proximity_group(controlsdb, proximity_group_name, side):
    proximity_group = get_proximity_group_by_properties(
        controlsdb, proximity_group_name, side
    )
    query = (
        "SELECT * FROM Control WHERE controlID IN "
        "(SELECT controlID FROM ProximityGroupControl WHERE proximitygroupID=:proximitygroupID)"
    )
    controlsdb.cursor.execute(
        query, {"proximitygroupID": proximity_group.proximitygroupID}
    )

    controls = list()
    for each in controlsdb.cursor:
        if not __controls.get(each["controlID"]):
            __controls[each["controlID"]] = Control.from_data(controlsdb, each)
        controls.append(__controls[each["controlID"]])
    if len(controls) >= 1:
        return controls
    return None


def get_control_horizontal_match(controlsdb, controlID):
    query = (
        "SELECT * FROM HorizontalMatch WHERE controlID=:controlID OR matchID=:controlID"
    )
    result = controlsdb.cursor.execute(query, {"controlID": controlID}).fetchall()
    horizontal_match = list()
    for each in result:
        if each["controlID"] == controlID:
            horizontal_match.append(get_control(controlsdb, each["matchID"]))
        elif each["matchID"] == controlID:
            horizontal_match.append(get_control(controlsdb, each["controlID"]))

    if len(horizontal_match) >= 1:
        return horizontal_match
    return None


def get_control_vertical_match(controlsdb, controlID):
    query = (
        "SELECT * FROM VerticalMatch WHERE controlID=:controlID OR matchID=:controlID"
    )
    result = controlsdb.cursor.execute(query, {"controlID": controlID}).fetchall()
    vertical_match = list()
    for each in result:
        if each["controlID"] == controlID:
            vertical_match.append(get_control(controlsdb, each["matchID"]))
        elif each["matchID"] == controlID:
            vertical_match.append(get_control(controlsdb, each["controlID"]))

    if len(vertical_match) >= 1:
        return vertical_match
    return None


def reset_controls():
    __controls.clear()

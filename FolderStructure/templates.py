# coding=utf-8
from __future__ import absolute_import, print_function

import re
import json
import os
import sys
import functools
from copy import deepcopy
from collections import defaultdict


from folderstructure.serialize import Serializable
from folderstructure.tokens import get_token
from folderstructure.logger import logger
from folderstructure.error import SolvingError, ParsingError, TemplateError

__templates = {'_active': None}


class Template(Serializable):
    """
    Each Template is managed by an instance of this class. Fields exist for each
    Token used in the template definition.

    Templates will assume not passed field values as values themselves. So
    'harcoded' values, so common in folder structure naming, can also be solved.
    e.g.: {project_name}\\CFG with passed values project_name=my_project, will
    return my_project\\CFG

    ``name`` (str): Unique name to identify this template.

    ``pattern`` (str): The template pattern to use, which uses existing Tokens.
    e.g.: '{projects_root}/{project}/{division}/Pipe/CFG/config.json'

    ``anchor`` ([ANCHOR_START, ANCHOR_END, ANCHOR_BOTH], optional): For parsing, regex matching
    will look for a match from this Anchor. If a pattern is anchored to the start, it requires
    the start of a passed path to match the pattern. Defaults to ANCHOR_START.
    """

    __FIELDS_REGEX = re.compile(r'{(.+?)}')
    __TEMPLATE_REFERENCE_REGEX = re.compile(r'{@(?P<reference>.+?)}')
    __STRIP_EXPRESSION_REGEX = re.compile(r'{(.+?)(:(\\}|.)+?)}')

    ANCHOR_START, ANCHOR_END, ANCHOR_BOTH = (1, 2, 3)

    def __init__(self, name, pattern, anchor=ANCHOR_START):
        super(Serializable, self).__init__()
        self.__name = name
        self.__anchor = anchor
        self.__at_code = '_WXV_'
        self.__pattern = self.__init_pattern(pattern)

    def data(self):
        """Collect all data for this object instance.

        Returns:
            dict: {attribute:value}
        """
        retval = dict()
        retval["_Serializable_classname"] = type(self).__name__
        retval["_Serializable_version"] = "1.0"
        retval["pattern"] = self.__pattern
        retval["anchor"] = self.__anchor
        retval["name"] = self.__name
        return retval

    @classmethod
    def from_data(cls, data):
        """Create object instance from give data. Used by Rule,
        Token, Separator to create object instances from disk saved data.

        Args:
            ``data`` (dict): {attribute:value}

        Returns:
            Serializable: Object instance for Rule, Token or Separator.
        """
        # Validation
        if data.get("_Serializable_classname") != cls.__name__:
            return None
        del data["_Serializable_classname"]
        if data.get("_Serializable_version") is not None:
            del data["_Serializable_version"]

        this = cls(
            data.get("name"), data.get("pattern"), data.get("anchor")
        )

        return this

    def solve(self, **values):
        """Given arguments are used to build a path. If no value is specified,
        the field name itself is used as value.

        Returns:
            str: A string with the resulting name.
        """
        # Make sure backslashes are slashes for pattern matching
        for key, value in values.items():
            if value is None:
                raise SolvingError(
                    "Token {} value passed is None.".format(key)
                )
            if "\\" in value:
                values[key] = value.replace("\\", "/")

        result = None
        try:
            result = self.__digits_pattern().format(**values)
        except KeyError as why:
            raise SolvingError(
                "Arguments passed do not match with template fields {}\n{}".format(
                    self.expanded_pattern(), why
                )
            )

        return result

    def parse(self, path):
        """Build and return dictionary with keys as tokens and values as given names.

        If your path uses the same token more than once, the returned dictionary keys
        will have the token name and an incremental digit next to them so they can be
        differentiated.

        Args:
            ``path`` (str): Path string.
            e.g.: "Y:/Projects/KillM/ART/VAULT/AVATARS/Male/Boots/Published/Rigging"

        Returns:
            dict: A dictionary with keys as tokens and values as given name parts.
            e.g.:
            {"projects_root":"Y:/Projects",
            "project":"KillM",
            "division":"ART",
            "assembly_type":"AVATARS",
            "assembly":"Male",
            "component":"Boots",
            "pipeline_step":"Rigging"}
        """
        # Make sure backslashes are slashes for pattern matching
        if "\\" in path:
            path = path.replace("\\", "/")

        # Build regular expresion for expanded pattern (including references)
        regex = self.__build_regex()
        parsed = dict()
        match = regex.search(path)
        if match:
            path_parts = sorted(match.groupdict().items())
            logger.debug(
                "Name parts: {}".format(
                    ", ".join(["('{}': '{}')".format(k[:-3], v) for k, v in path_parts])
                )
            )
            repeated_fields = dict()
            for each in self.fields:
                if each not in repeated_fields.keys():
                    if self.fields.count(each) > 1:
                        repeated_fields[each] = 1
            if repeated_fields:
                logger.debug(
                    "Repeated tokens: {}".format(", ".join(repeated_fields.keys()))
                )

            for key, value in path_parts:
                # Strip number that was added to make group name unique
                token_name = key[:-3]
                token = get_token(token_name)
                # Make sure backslashes are slashes for pattern matching
                if "\\" in value or "/" in value:
                    value = os.path.normpath(value)
                if token_name in repeated_fields.keys():
                    counter = repeated_fields.get(token_name)
                    repeated_fields[token_name] = counter + 1
                    token_name = "{}{}".format(token_name, counter)
                parsed[token_name] = token.parse(value)
            return parsed
        else:
            raise ParsingError(
                "Path did not match template '{}' pattern. Path={} Pattern={}".format(
                    self.name, path, self.expanded_pattern()
                )
            )

    def __build_regex(self):
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        # Escape non-placeholder components
        expression = re.sub(
            r'(?P<placeholder>{(.+?)(:(\\}|.)+?)?})|(?P<other>.+?)',
            self.__escape,
            self.expanded_pattern()
        )
        # Replace placeholders with regex pattern
        expression = re.sub(
            r'{(?P<placeholder>.+?)(:(?P<expression>(\\}|.)+?))?}',
            functools.partial(
                self.__convert, placeholder_count=defaultdict(int)
            ),
            expression
        )

        if self.__anchor is not None:
            if bool(self.__anchor & self.ANCHOR_START):
                expression = '^{0}'.format(expression)

            if bool(self.__anchor & self.ANCHOR_END):
                expression = '{0}$'.format(expression)
        # Compile expression
        try:
            compiled = re.compile(expression)
        except re.error as error:
            if any([
                'bad group name' in str(error),
                'bad character in group name' in str(error)
            ]):
                raise ValueError('Placeholder name contains invalid characters.')
            else:
                _, value, traceback = sys.exc_info()
                message = 'Invalid pattern: {0}'.format(value)
                if sys.version_info[0] == 3:
                    raise ValueError(message).with_traceback(traceback)
                elif sys.version_info[0] == 2:
                    raise ValueError(message, traceback)

        return compiled

    def __convert(self, match, placeholder_count):
        """Return a regular expression to represent *match*.

        ``placeholder_count`` should be a ``defaultdict(int)`` that will be used to
        store counts of unique placeholder names.

        """
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        placeholder_name = match.group('placeholder')

        # Support at symbol (@) as referenced template indicator. Currently,
        # this symbol not a valid character for a group name in the standard
        # Python regex library. Rather than rewrite or monkey patch the library
        # work around the restriction with a unique identifier.
        placeholder_name = placeholder_name.replace('@', self.__at_code)

        # The re module does not support duplicate group names. To support
        # duplicate placeholder names in templates add a unique count to the
        # regular expression group name and strip it later during parse.
        placeholder_count[placeholder_name] += 1
        placeholder_name += '{0:03d}'.format(
            placeholder_count[placeholder_name]
        )

        expression = match.group('expression')
        if expression is None:
            expression = r'[\w_.\-/:]+'

        # Un-escape potentially escaped characters in expression.
        expression = expression.replace('{', '{').replace('}', '}')

        return r'(?P<{0}>{1})'.format(placeholder_name, expression)

    def expanded_pattern(self):
        """Return pattern with all referenced templates expanded recursively.

        Returns:
            [str]: Pattern with all referenced templates expanded recursively.
        """
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        return self.__TEMPLATE_REFERENCE_REGEX.sub(
            self.__expand_reference, self.pattern
        )

    def expanded_pattern_validation(self, pattern):
        """Return pattern with all referenced templates expanded recursively from a given pattern

        Args:
            ``pattern`` (str): Pattern string.
            e.g.: "{@template_base}/{token_1}/{token_2}/inmutable_folder/"

        Returns:
            [str]: Pattern with all referenced templates expanded recursively.
        """
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        return self.__TEMPLATE_REFERENCE_REGEX.sub(
            self.__expand_reference, pattern
        )

    def __expand_reference(self, match):
        """Expand reference represented by *match*.

        Args:
            match (str): Template name to look for in repo.

        Raises:
            TemplateError: If pattern contains a reference that cannot be
            resolved.

        Returns:
            [str]: Expanded reference pattern
        """
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        reference = match.group('reference')

        template = get_template(reference)
        if template is None:
            raise TemplateError(
                'Failed to find reference {} in current repo.'.format(reference)
            )

        return template.expanded_pattern()

    def __escape(self, match):
        """Escape matched 'other' group value."""
        # ? Taken from Lucidity by Martin Pengelly-Phillips
        groups = match.groupdict()
        if groups['other'] is not None:
            return re.escape(groups['other'])

        return groups['placeholder']

    def __digits_pattern(self):
        # * This accounts for those cases where a token is used more than once in a rule
        digits_pattern = deepcopy(self.expanded_pattern())
        for each in list(set(self.fields)):
            # ? This is going to be a bit more difficult to handle when nesting templates
            # ? due to the . character not being contemplated by the pattern
            regex_pattern = re.compile("{{{0}}}".format(each))
            indexes = [match.end() for match in regex_pattern.finditer(digits_pattern)]
            repetitions = len(indexes)
            if repetitions > 1:
                i = 0
                for match in sorted(indexes, reverse=True):
                    digits_pattern = "{}{}{}".format(
                        digits_pattern[:match-1],
                        str(repetitions-i),
                        digits_pattern[match-1:]
                    )
                    i += 1
        logger.debug("Digits pattern to account for repeated fields: {}".format(digits_pattern))
        return digits_pattern

    def __init_pattern(self, pattern):
        new_pattern = pattern
        backslash = '\\'
        slash = '/'
        if backslash in pattern:
            new_pattern = pattern.replace(backslash, slash)
            logger.debug("Replaced '\\' with '/' in pattern.\n"
                         "Old pattern: {}\n"
                         "New pattern: {}".format(
                            pattern, new_pattern)
                         )
        return new_pattern

    @property
    def pattern(self):
        """
        Returns:
            [str]: Pattern that this Template was initialized with.
        """
        return self.__pattern

    @pattern.setter
    def pattern(self, pattern):
        """
        Some times we need to change the pattern dinamically, at runtime.
        """
        self.__pattern = self.__init_pattern(pattern)

    @property
    def fields(self):
        """
        Returns:
            [tuple]: Tuple of all Tokens found in this Template's pattern
        """
        return tuple(self.__FIELDS_REGEX.findall(self.expanded_pattern()))

    @property
    def name(self):
        """
        Returns:
            [str]: Name of this Template
        """
        return self.__name

    @property
    def anchor(self):
        """
        Returns:
            [int]: Template.ANCHOR_START, Template.ANCHOR_END, Template.ANCHOR_BOTH = (1, 2, 3)
        """
        return self.__anchor

    @anchor.setter
    def anchor(self, a):
        """
        Args:
            [int]: Template.ANCHOR_START, Template.ANCHOR_END, Template.ANCHOR_BOTH
        """
        self.__anchor = a

    @name.setter
    def name(self, n):
        """
        Args:
            [str]: Set name of this Template
        """
        self.__name = n


def add_template(name, pattern, anchor=Template.ANCHOR_START):
    """Add template to current folder structure session. If no active template is found, it adds
    the created one as active by default.

    Args:
        ``name`` (str): Name that best describes the template, this will be used as a way
        to invoke the Template object.

        ``pattern`` (str): The template pattern to use, which uses existing Tokens.
        e.g.: '{projects_root}/{project}/{division}/Pipe/CFG/config.json'

        ``anchor``: ([Template.ANCHOR_START, Template.ANCHOR_END, Template.ANCHOR_BOTH], optional):
        For parsing, regex matching will look for a match from this Anchor. If a
        pattern is anchored to the start, it requires the start of a passed path to
        match the pattern. Defaults to ANCHOR_START.

    Returns:
        Template: The Template object instance created for given name and fields.
    """
    template = Template(name, pattern, anchor)
    __templates[name] = template
    if get_active_template() is None:
        set_active_template(name)
        logger.debug("No active template found, setting this one as active: {}".format(name))
    return template


def remove_template(name):
    """Remove Template from current session.

    Args:
        name (str): The name of the template to be removed.

    Returns:
        bool: True if successful, False if a template name was not found.
    """
    if has_template(name):
        del __templates[name]
        return True
    return False


def has_template(name):
    """Test if current session has a template with given name.

    Args:
        name (str): The name of the template to be looked for.

    Returns:
        bool: True if template with given name exists in current session, False otherwise.
    """
    return name in __templates.keys()


def update_template_name(old_name, new_name):
    """Update template name.

    Args:
        old_name (str): The current name of the template to update.

        new_name (str): The new name of the template to be updated.

    Returns:
        True if Template name was updated, False if another template
        has that name already or no current template with old_name was found.
    """
    if has_template(old_name) and not has_template(new_name):
        template_obj = __templates.pop(old_name)
        template_obj.name = new_name
        __templates[new_name] = template_obj
        if __templates.get("_active") == old_name:
            __templates["_active"] == new_name
        return True
    return False


def reset_templates():
    """Clears all templates created for current session.

    Returns:
        bool: True if clearing was successful.
    """
    __templates.clear()
    __templates['_active'] = None
    return True


def get_active_template():
    """Get currently active template for the session. This is the template
    that will be used to parse and solve from.

    Returns:
        Template: Template object instance for currently active Template.
    """
    name = __templates.get('_active')
    return __templates.get(name)


def set_active_template(name):
    """Sets given template as active for the session. This it the template that's
    being used to parse and solve from.

    Args:
        name (str): The name of the template to be activated.

    Returns:
        bool: True if successful, False otherwise.
    """
    if has_template(name):
        __templates['_active'] = name
        return True
    return False


def get_template(name):
    """Gets Template object with given name.

    Args:
        name (str): The name of the template to query.

    Returns:
        Template: Template object instance for given name.
    """
    return __templates.get(name)


def get_templates():
    """Get all template objects for current session.

    Returns:
        dict: {template_name:Template}
    """
    templates_copy = deepcopy(__templates)
    del templates_copy["_active"]
    return templates_copy


def validate_template_pattern(name):
    """Validates template pattern is not empty.

    Args:
        name (str): The name of the template to validate its pattern.

    Returns:
        bool: True if successful, False otherwise.
    """
    if has_template(name):
        template_obj = get_template(name)
        if len(template_obj.pattern) >= 1:
            return True
    return False


def validate_templates():
    not_valid = list()
    for name, template in get_templates().items():
        if not validate_template_pattern(name):
            not_valid.append(name)
    if len(not_valid) >= 1:
        raise TemplateError(
            "Templates '{}': Patterns are not valid.".format(', '.join(not_valid))
        )


def save_template(name, directory):
    """Saves given template serialized to specified location.

    Args:
        ``name`` (str): The name of the template to be saved.

        ``directory`` (str): Path location to save the template.

    Returns:
        bool: True if successful, False if template wasn't found in current session.
    """
    template = get_template(name)
    if not template:
        return False
    file_name = "{}.template".format(name)
    filepath = os.path.join(directory, file_name)
    with open(filepath, "w") as fp:
        json.dump(template.data(), fp)
    return True


def load_template(filepath):
    """Load template from given location and create Template object in memory to work with it.

    Args:
        filepath (str): Path to existing .template file location

    Returns:
        bool: True if successful, False if .template wasn't found.
    """
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    new_template = Template.from_data(data)
    if new_template:
        __templates[new_template.name] = new_template
        return True
    return False

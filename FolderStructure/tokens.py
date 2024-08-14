# coding=utf-8
from __future__ import absolute_import, print_function

import copy
import json
import os


from folderstructure.serialize import Serializable
from folderstructure.logger import logger
from folderstructure.error import TokenError


__tokens = dict()


class Token(Serializable):
    """Tokens are the meaningful parts of a template. A token can be required,
    meaning fully typed by the user, or can have a set of default options preconfigured.
    If options are present, then one of them is the default one.
    Each option follows a {full_name:abbreviation} schema, so that names can be short
    but meaning can be recovered easily.

    Args:
        ``name`` (str): Name that best describes the Token, this will be used as a way
        to invoke the Token object.
    """
    def __init__(self, name):
        super(Token, self).__init__()
        self.__name = name
        self.__default = None
        self.__options = dict()

    def add_option(self, fullname, abbreviation):
        """Adds an option pair to this Token.

        Args:
            ``fullname`` (str): Full length name of the option.

            ``abbreviation`` (str): Abbreviation to be used when building the path.

        Returns:
            [bool]: True if successful. False otherwise.
        """
        if fullname not in self.__options.keys():
            self.__options[fullname] = abbreviation
            if len(self.__options) == 1:
                self.__default = fullname
            return True
        logger.debug(
            "Option '{}':'{}' already exists in Token '{}'. "
            "Use update_option() instead.".format(fullname, self.__options.get(fullname), self.__name)
        )
        return False

    def update_option(self, fullname, abbreviation):
        """Update an option pair on this Token.

        Args:
            ``fullname`` (str): Full length name of the option.

            ``abbreviation`` (str): Abbreviation to be used when building the path.

        Returns:
            [bool]: True if successful. False otherwise.
        """
        if fullname in self.__options.keys():
            self.__options[fullname] = abbreviation
            return True
        logger.debug(
            "Option '{}':'{}' doesn't exist in Token '{}'. "
            "Use add_option() instead.".format(fullname, self.__options.get(fullname), self.__name)
        )
        return False

    def remove_option(self, fullname):
        """Remove an option on this Token.

        Args:
            ``fullname`` (str): Full name of the option

        Returns:
            [bool]: True if successful. False otherwise.
        """
        if fullname in self.__options.keys():
            del self.__options[fullname]
            return True
        logger.debug(
            "Option '{}':'{}' doesn't exist in Token '{}'. ".format(
                fullname, self.__options.get(fullname), self.__name
            )
        )
        return False

    def clear_options(self):
        """Clears all the options for this token.
        """
        self.__default = None
        self.__options = dict()

    def has_option_fullname(self, fullname):
        """Looks for given option full name in the options.

        Args:
            ``fullname`` (str): Full name of the option

        Returns:
            [bool]: True if found. False otherwise.
        """
        if fullname in self.__options.keys():
            return True
        return False

    def has_option_abbreviation(self, abbreviation):
        """Looks for given option abbreviation in the options.

        Args:
            ``abbreviation`` (str): Abbreviation

        Returns:
            [bool]: True if found. False otherwise.
        """
        if abbreviation in self.__options.values():
            return True
        return False

    def solve(self, name=None):
        """Solve for abbreviation given a certain name. e.g.: 'center' could return 'C'

        Args:
            ``name`` (str, optional): Key to look for in the options for this Token.
            Defaults to None, which will return the default value set in the options
            for this Token.

        Raises:
            TokenError: If Token is required and no value is passed.

            TokenError: If given name is not found in options list.

        Returns:
            str: If Token is required, the same input value is returned.

            str: If Token has options, the abbreviation for given name is returned.

            str: If nothing is passed and Token has options, default option is returned.
        """
        if self.required and name:
            return name
        elif self.required and name is None:
            raise TokenError("Token {} is required. name parameter must be passed.".format(self.__name))
        elif not self.required and name:
            if name not in self.__options.keys():
                raise TokenError(
                    "name '{}' not found in Token '{}'. Options: {}".format(
                        name, self.__name, ', '.join(self.__options.keys())
                        )
                    )
            return self.__options.get(name)
        elif not self.required and not name:
            return self.__options.get(self.default)

    def parse(self, value):
        """Get metatada (origin) for given value in name. e.g.: L could return left

        Args:
            ``value`` (str): Name part to be parsed to the token origin

        Returns:
            str: Token origin for given value or value itself if no match is found.
        """
        if self.required:
            return value
        elif not self.required and len(self.__options) >= 1:
            for k, v in self.__options.items():
                if v == value:
                    return k
        raise TokenError("Value '{}' not found in Token '{}'. Options: {}".format(
                value, self.__name, ', '.join(self.__options.values())
            )
        )

    @property
    def required(self):
        """
        Returns:
            [bool]: True if Token is required, False otherwise
        """
        return self.default is None

    @property
    def name(self):
        """
        Returns:
            [str]: Name of this Token
        """
        return self.__name

    @name.setter
    def name(self, n):
        """
        Returns:
            [str]: Set name of this Template
        """
        self.__name = n

    @property
    def default(self):
        """If Token has options, one of them will be default. Either passed by the user,
        or simply the first found item in options.

        Returns:
            [str]: Default option value.
        """
        if self.__default is None and len(self.__options) >= 1:
            self.__default = sorted(list(self.__options.keys()))[0]
        return self.__default

    @default.setter
    def default(self, d):
        """
        Args:
            d (str): Value of the default option to be set
        """
        self.__default = d

    @property
    def options(self):
        """
        Returns:
            [dict]: {"option_full_name":"abbreviation"}
        """
        return copy.deepcopy(self.__options)


def add_token(token_name, **kwargs):
    """Add token to current naming session. If 'default' keyword argument is found,
    set it as default for the token instance.

    Args:
        ``token_name`` (str): Name that best describes the token, this will be used as a way
        to invoke the Token object.

        kwargs: Each argument following the name is treated as an options for the
        new Token.

    Returns:
        Token: The Token object instance created for given name and fields.
    """
    token = Token(token_name)
    for k, v in kwargs.items():
        if k == "default":
            continue
        token.add_option(k, v)
    if "default" in kwargs.keys():
        extract_default = copy.deepcopy(kwargs)
        del extract_default["default"]
        if kwargs.get('default') in extract_default.keys():
            token.default = kwargs.get('default')
        elif kwargs.get('default') in extract_default.values():
            for k, v in extract_default.items():
                if v == kwargs.get('default'):
                    token.default = k
                    break
        else:
            raise TokenError("Default value must match one of the options passed.")
    __tokens[token_name] = token
    return token


def remove_token(token_name):
    """Remove Token from current session.

    Args:
        ``token_name`` (str): The name of the token to be removed.

    Returns:
        bool: True if successful, False if a token name was not found.
    """
    if has_token(token_name):
        del __tokens[token_name]
        return True
    return False


def has_token(token_name):
    """Test if current session has a token with given name.

    Args:
        ``token_name`` (str): The name of the token to be looked for.

    Returns:
        bool: True if token with given name exists in current session, False otherwise.
    """
    return token_name in __tokens.keys()


def update_token_name(old_name, new_name):
    """Update token name.

    Args:
        old_name (str): The current name of the token to update.

        new_name (str): The new name of the token to be updated.

    Returns:
        True if Token name was updated, False if another token
        has that name already or no current template with old_name was found.
    """
    if has_token(old_name) and not has_token(new_name):
        token_obj = __tokens.pop(old_name)
        token_obj.name = new_name
        __tokens[new_name] = token_obj
        if __tokens.get("_active") == old_name:
            __tokens["_active"] == new_name
        return True
    return False


def reset_tokens():
    """Clears all tokens created for current session.

    Returns:
        bool: True if clearing was successful.
    """
    __tokens.clear()
    return True


def get_token(token_name):
    """Gets Token object with given name.

    Args:
        ``token_name`` (str): The name of the token to query.

    Returns:
        Token: Token object instance for given name.
    """
    return __tokens.get(token_name)


def get_tokens():
    """Get all Token and TokenNumber objects for current session.

    Returns:
        dict: {token_name:token_object}
    """
    return __tokens


def get_token_options(token_name):
    """Gets Token options for given token

    Args:
        ``token_name`` (str): The name of the token to query.

    Returns:
        [dict]: Token options. None if no token with given name was found,
        or token has no options.
    """
    if has_token(token_name):
        token_obj = get_token(token_name)
        return token_obj.options
    return None


def get_token_default_option(token_name):
    """Gets Token default option for given token

    Args:
        ``token_name`` (str): The name of the token to query.

    Returns:
        [dict]: Token default option. None if no token with given name was found,
        or token has no options.
    """
    if has_token(token_name):
        token_obj = get_token(token_name)
        option_dict = {token_obj.default: token_obj.options.get(token_obj.default)}
        return option_dict
    return None


def add_option_to_token(token_name, fullname, abbreviation):
    """Adds an option pair to this Token.

    Args:
        ``token_name`` (str): The name of the exisiting token.

        ``fullname`` (str): Full length name of the option.

        ``abbreviation`` (str): Abbreviation to be used when building the path.

    Returns:
        [bool]: True if successful. False otherwise.
    """
    if has_token(token_name):
        token_obj = get_token(token_name)
        return token_obj.add_option(fullname, abbreviation)
    return False


def update_option_fullname_from_token(token_name, old_fullname, new_fullname):
    """Update an option fullname on this Token.

    Args:
        ``token_name`` (str): The name of the exisiting token.

        ``old_fullname`` (str): Old full length name of the option.

        ``new_fullname`` (str): New full length name of the option.

        ``abbreviation`` (str): Abbreviation to be used when building the path.

    Returns:
        [bool]: True if successful. False otherwise.
    """
    if has_token(token_name):
        token_obj = get_token(token_name)
        if token_obj.has_option_fullname(old_fullname):
            abbreviation = token_obj.options.get(old_fullname)
            token_obj.remove_option(old_fullname)
            return token_obj.add_option(new_fullname, abbreviation)
    return False


def update_option_abbreviation_from_token(token_name, fullname, abbreviation):
    """Update an option abbreviation on this Token.

    Args:
        ``token_name`` (str): The name of the exisiting token.

        ``fullname`` (str): Full length name of the option.

        ``abbreviation`` (str): Abbreviation to be used when building the path.

    Returns:
        [bool]: True if successful. False otherwise.
    """
    if has_token(token_name):
        token_obj = get_token(token_name)
        if token_obj.has_option_fullname(fullname):
            return token_obj.update_option(fullname, abbreviation)
    return False


def remove_option_from_token(token_name, fullname):
    """Remove an option on given token.

    Args:
        ``token_name`` (str): The name of the exisiting token.

        ``fullname`` (str): Full length name of the option

    Returns:
        [bool]: True if successful. False otherwise.
    """
    if has_token(token_name):
        token_obj = get_token(token_name)
        if token_obj.has_option_fullname(fullname):
            return token_obj.remove_option(fullname)
    return False


def has_option_fullname(token_name, fullname):
    """Looks for given option full name in the given token options.

    Args:
        ``fullname`` (str): Full name of the option

    Returns:
        [bool]: True if found. False otherwise.
    """
    if has_token(token_name):
        token_obj = get_token(token_name)
        return token_obj.has_option_fullname(fullname)
    return False


def has_option_abbreviation(token_name, abbreviation):
    """Looks for given option abbreviation in the given token options.

        Args:
            ``abbreviation`` (str): Abbreviation

        Returns:
            [bool]: True if found. False otherwise.
        """
    if has_token(token_name):
        token_obj = get_token(token_name)
        return token_obj.has_option_abbreviation(abbreviation)
    return False


def validate_tokens():
    not_valid = list()
    for name, token_obj in get_tokens().items():
        if not token_obj.required and len(token_obj.options) == 0:
            not_valid.append(name)
    if len(not_valid) >= 1:
        raise TokenError(
            "Tokens '{}': Not required tokens must "
            "have at least one option (fullname=abbreviation).".format(', '.join(not_valid))
        )


def save_token(name, directory):
    """Saves given token serialized to specified location.

    Args:
        ``name`` (str): The name of the token to be saved.

        ``directory`` (str): Path location to save the token.

    Returns:
        bool: True if successful, False if token wasn't found in current session.
    """
    token_obj = get_token(name)
    if not token_obj:
        return False
    file_name = "{}.token".format(name)
    filepath = os.path.join(directory, file_name)
    with open(filepath, "w") as fp:
        json.dump(token_obj.data(), fp)
    return True


def load_token(filepath):
    """Load token from given location and create Token object in memory to work with it.

    Args:
        ``filepath`` (str): Path to existing .token file location

    Returns:
        bool: True if successful, False if .token wasn't found or python object
        couldn't be created.
    """
    if not os.path.isfile(filepath):
        return False
    try:
        with open(filepath) as fp:
            data = json.load(fp)
    except Exception:
        return False
    new_token = Token.from_data(data)
    if new_token:
        __tokens[new_token.name] = new_token
        return True
    return False

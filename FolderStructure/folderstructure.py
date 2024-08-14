# coding=utf-8
from __future__ import absolute_import, print_function

import re
import os
import sys
import json
import shutil

from folderstructure import templates
from folderstructure import tokens
from folderstructure.error import RepoError, SolvingError
from folderstructure.logger import logger

FOLDERSTRUCTURE_REPO_ENV = "FOLDERSTRUCTURE_REPO"


def parse(path):
    """Get metadata from a path string recognized by the currently active template.

    Args:
        ``path`` (str): Path string e.g.: C:/thisproject/thisasset/model

    Returns:
        [dict]: A dictionary with keys as tokens and values as given path parts.
        e.g.: {'project':'thisproject', 'asset':'thisasset', 'pipestep': 'model'}
    """
    template = templates.get_active_template()
    return template.parse(path)


def solve(*args, **kwargs):
    """Given arguments are used to build a path following the currently active template.

    Raises:
        TokenError: A required token was passed as None to keyword arguments.

        SolvingError: Missing argument for one field in currently active template.

    Returns:
        [str]: A string with the resulting name.
    """
    template = templates.get_active_template()
    # * This accounts for those cases where a token is used more than once in a template
    repeated_fields = dict()
    for each in template.fields:
        if each not in repeated_fields.keys():
            if template.fields.count(each) > 1:
                repeated_fields[each] = 1
    fields_with_digits = list()
    for each in template.fields:
        if each in repeated_fields.keys():
            counter = repeated_fields.get(each)
            repeated_fields[each] = counter + 1
            fields_with_digits.append("{}{}".format(each, counter))
        else:
            fields_with_digits.append(each)
    values = dict()
    i = 0
    fields_inc = 0
    for f in fields_with_digits:
        token = tokens.get_token(template.fields[fields_inc])
        if token:
            # Explicitly passed as keyword argument
            if kwargs.get(f) is not None:
                values[f] = token.solve(kwargs.get(f))
                fields_inc += 1
                continue
            # Explicitly passed as keyword argument without repetitive digits
            # Use passed argument for all field repetitions
            elif kwargs.get(template.fields[fields_inc]) is not None:
                values[f] = token.solve(kwargs.get(template.fields[fields_inc]))
                fields_inc += 1
                continue
            elif token.required and kwargs.get(f) is None and len(args) == 0:
                raise SolvingError(
                    "Token '{}' is required but was not passed.".format(token.name)
                )
            # Not required and not passed as keyword argument, get default
            elif not token.required and kwargs.get(f) is None:
                values[f] = token.solve()
                fields_inc += 1
                continue
            # Implicitly passed as positional argument
            try:
                values[f] = token.solve(args[i])
                i += 1
                fields_inc += 1
                continue
            except IndexError as why:
                raise SolvingError(
                    "Missing argument for field '{}'\n{}".format(f, why)
                )
    logger.debug(
        "Solving template {} with values {}".format(template.name, values)
    )
    return template.solve(**values)


def validate_repo(repo):
    config_file = os.path.join(repo, "folderstructure.conf")
    if not os.path.exists(config_file):
        return False
    return True


def validate_tokens_and_referenced_templates(pattern):
    valid = True

    regex = re.compile(r'{(?P<placeholder>.+?)(:(?P<expression>(\\}|.)+?))?}')
    matches = regex.finditer(pattern)

    total_templates = list(templates.get_templates().keys())
    total_tokens = list(tokens.get_tokens().keys())

    templates_used = list()
    tokens_used = list()
    for match in matches:
        match_text = match.group(1)
        if match_text.startswith("@"):
            templates_used.append(match_text.replace("@", ""))
        else:
            tokens_used.append(match_text)

    for template_use in templates_used:
        if template_use not in total_templates:
            valid = False
            break

    for token_use in tokens_used:
        if token_use not in total_tokens:
            valid = False
            break

    return valid


def get_repo(force_repo=None):
    """Get the path to a folder structures repo.

    Path is looked for in these places and with the given priority:

        1- ``force_repo`` parameter

        2- Environment variable: FOLDERSTRUOCTURE_REPO

        3- User config file: C:/Users/xxxxx/.NXATools/nxacore/config.json

        4- Dev config file: __file__/cfg/config.json

    In both config.json files the key it looks for is 'folderstructure_repo'

    If a root path is passed as ``force_repo`` parameter, then it'll
    return the same path but first checks it actually exists.

    Keyword Arguments:
        ``force_repo`` {str} -- Use this path instead of looking for
        pre-configured ones (default: {None})

    Raises:
        RepoError: Given repo directory does not exist.

        RepoError: Config file for folderstructure library couldn't be found.

    Returns:
        [str] -- Root path

        [None] -- If path doesn't exist or config file wasn't found in
        pre-configured paths. Use folderstructure.logger.init_logger() to get
        more details.
    """
    # Env level
    env_root = os.environ.get(FOLDERSTRUCTURE_REPO_ENV)

    # User level
    user_cfg_path = os.path.join(
        os.path.expanduser("~"), ".NXATools", "folderstructure", "config.json"
    )
    user_config = dict()
    if os.path.exists(user_cfg_path):
        with open(user_cfg_path) as fp:
            user_config = json.load(fp)
    user_root = user_config.get("folderstructure_repo")

    root = env_root or user_root
    if force_repo:
        root = force_repo

    if not validate_repo(root):
        raise RepoError("Folder structure repo is not valid, missing config files.")

    if root:
        root_real_path = os.path.realpath(root)
        if os.path.exists(root_real_path):
            logger.debug("Folder Structure repo: {}".format(root_real_path))
            return root_real_path
        else:
            raise RepoError("Folder Structure repo directory doesn't exist: {}".format(root_real_path))

    raise RepoError("Config file not found in {}".format(root))


def save_session(repo=None, override=True):
    """Save templates, tokens and config files to the repository.

    Raises:
        RepoError: Repository directory could not be created or is not valid.

        TokenError: Not required tokens must have at least one option (fullname=abbreviation).

        TemplateError: Template patterns are not valid.

    Args:
        ``repo`` (str, optional): Absolue path to a repository. Defaults to None.

        ``override`` (bool, optional): If True, it'll remove given directory and recreate it.

    Returns:
        [bool]: True if saving session operation was successful.
    """
    # Validations
    templates.validate_templates()
    tokens.validate_tokens()

    repo = repo or get_repo()
    if override:
        try:
            shutil.rmtree(repo)
        except (IOError, OSError) as why:
            traceback = sys.exc_info()[2]
            raise RepoError(why, traceback)
    if not os.path.exists(repo):
        try:
            os.mkdir(repo)
        except (IOError, OSError) as why:
            traceback = sys.exc_info()[2]
            raise RepoError(why, traceback)

    # save tokens
    for name, token in tokens.get_tokens().items():
        logger.debug("Saving token: {} in {}".format(name, repo))
        tokens.save_token(name, repo)
    # save templates
    for name, template in templates.get_templates().items():
        if not isinstance(template, templates.Template):
            continue
        logger.debug("Saving template: {} in {}".format(name, repo))
        templates.save_template(name, repo)
    # extra configuration
    active = templates.get_active_template()
    config = {"set_active_template": active.name if active else None}
    filepath = os.path.join(repo, "folderstructure.conf")
    logger.debug("Saving active template: {} in {}".format(active.name, filepath))
    with open(filepath, "w") as fp:
        json.dump(config, fp, indent=4)
    return True


def load_session(repo=None):
    """Load templates, tokens and config from a repository, and create
    Python objects in memory to work with them.

    Args:
        ``repo`` (str, optional): Absolute path to a repository. Defaults to None.

    Returns:
        [bool]: True if loading session operation was successful.
    """
    repo = repo or get_repo()
    if not os.path.exists(repo):
        logger.warning("Given repo directory does not exist: {}".format(repo))
        return False
    namingconf = os.path.join(repo, "folderstructure.conf")
    if not os.path.exists(namingconf):
        logger.warning("Repo is not valid. folderstructure.conf not found {}".format(namingconf))
        return False
    # tokens and templates
    for dirpath, dirnames, filenames in os.walk(repo):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if filename.endswith(".token"):
                logger.debug("Loading token: {}".format(filepath))
                tokens.load_token(filepath)
            elif filename.endswith(".template"):
                logger.debug("Loading template: {}".format(filepath))
                templates.load_template(filepath)
    # extra configuration
    if os.path.exists(namingconf):
        logger.debug("Loading active template: {}".format(namingconf))
        with open(namingconf) as fp:
            config = json.load(fp)
        templates.set_active_template(config.get('set_active_template'))
    return True

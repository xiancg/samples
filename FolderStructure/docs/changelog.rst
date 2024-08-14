Changelog
================================

1.3.7-beta
---------------------------------------

**Update:**
    - Adds the "Save Session And Close" button

**Bug fixes:**
    - Fix an error when the extended pattern is empty


1.3.6-beta
---------------------------------------

**Update:**
    - Adds the expanded path validator
    - Improve general UX

**Bug fixes:**
    - Clean code and adapts to PEP8 standard
    - Fix when adding a NEW_TOKEN and name wasn't changed
    - Fix loading session when creating a new repository
    - Fix setting the default option token from abbreviation cell
    - Cleanup options when resetting tokens
    - Fix status bar calls
    - Fix pattern when adding a new template
    - Fix when you add a new template and is the only one, set as default


1.3.5-beta
---------------------------------------

**Update:**
    - Refactor dialog launch functions

1.3.4-beta
---------------------------------------

**Update:**
    - Adds the possibility to pass a parent

1.3.3-beta
---------------------------------------

**Update:**
    - Add the Anchor edit to templates

1.3.2-beta
---------------------------------------

**Bug fix:**
    - Remove logic to create dialog instance to favor instancing directly from the FolderStruct_GUI class

1.3.1-beta
---------------------------------------

**Bug fix:**
    - Remove not used references

1.3.0-beta
---------------------------------------

**Feature:**
    - GUI implementation to interact with folder structure sessions

1.2.10-beta
---------------------------------------

**Bug fix:**
    - Options len should be zero in validation.

1.2.9-beta
---------------------------------------

**Bug fix:**
    - Validations must happen before doing anything to the repo.

1.2.8-beta
---------------------------------------

**Bug fix:**
    - Validate not required tokens have at least one option before saving or raise error.
  
**Improvement:**
    - Add Token.clear_options().

1.2.7-beta
---------------------------------------

**Improvement:**
    - Adds pattern validation for all templates before saving session.
    - Implements override option for save_session

1.2.6-beta
---------------------------------------

**Bug fix:**
    - Remove unexistent import in package API.

1.2.5-beta
---------------------------------------

**Improvements:**
    - Add functions to update option fullname and abbreviations.
    - Add repo validation function

1.2.4-beta
---------------------------------------

**Improvements:**
    - Exposed errors in package API.

1.2.3-beta
---------------------------------------

**Improvements:**
    - Add functions to update Token and Template names

1.2.2-beta
---------------------------------------

**Improvements:**
    - Better logging when parsing doesn't work.
    - Refactor tests to modules and add tests for runtime changes in pattern.

1.2.1-beta
---------------------------------------

**Feature:**
    - Some times we need to change the pattern dynamically, at runtime. Super useful stuff.

1.1.4-beta
---------------------------------------

**Bug fix:**
    - Raise SolvingError if value passed to Token is None

1.1.3-beta
---------------------------------------

**Bug fix:**
    - Remove _active from returned data in get_templates and return a copy instead of the actual dict

1.1.1-beta
---------------------------------------

**Bug fix:**
    - Improve error message when token is required but not passed.

1.1.0-alpha
---------------------------------------

**Improvements:**
    - Adds support for referenced templates with "@"

1.0.5-alpha
---------------------------------------

**Improvements:**
    - Adds support for token repetitions in templates
    - Adds CRUD functions for options manipulation on tokens
    - Update docs

1.0.4-alpha
---------------------------------------

**Improvements:**
    - Added documentation for the entire package
    - Added custom errors

1.0.3-alpha
---------------------------------------

**Features:**
    - Parsing of metadata from paths
    - Solving paths using pre-established Templates and Tokens
    - Repository saving and loading of serialized Templates and Tokens
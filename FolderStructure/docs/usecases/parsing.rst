Parsing
=====================

Files and folder paths contain a bunch of metadata about what they store/organize. All of this metadata that can be read and used to our advantage. Each Token is basically a piece of metadata. Each Template helps us extract that metadata from paths.

.. note::
    The parsing function is folderstructure.parse(path)

.. warning::
    The appropiate Template must be set as active before calling the parse() function. Use folderstructure.set_active_template("template_name")

Let's set these Tokens and Template.

.. code-block:: python

    import folderstructure as fs

    # CREATE TOKENS
    fs.add_token("projects_root")
    fs.add_token("project")
    fs.add_token("division", DEV="DEV", ART="ART", PROD="PROD", default="ART")
    fs.add_token("asset_type", SETS="SETS", CHARACTERS="CHARACTERS", default="SETS")
    fs.add_token("asset")
    fs.add_token("component")
    fs.add_token(
        "pipeline_step",
        HighRes="HighRes", LowRes="LowRes", Rigging="Rigging", Scan="Scan", Texturing="Texturing",
        default="HighRes"
    )

    # CREATE TEMPLATES
    fs.add_template(
        "pipestep_vault",
        '{projects_root}/{project}/{division}/VAULT/{asset_type}/{asset}/{component}/Published/{pipeline_step}',
        anchor=fs.Template.ANCHOR_END
    )

    fs.set_active_template("pipestep_vault")

And then let's parse this path:

.. code-block:: python

    fs.parse("Y:/Projects/MyProject/ART/VAULT/CHARACTERS/Male/Boots/Published/Rigging")

The result will be the following dictionary with all the metadata extracted to key, value pairs:

.. code-block:: python

    result = {
        "projects_root":"Y:/Projects",
        "project":"MyProject",
        "division":"ART",
        "asset_type":"CHARACTERS",
        "asset":"Male",
        "component":"Boots",
        "pipeline_step":"Rigging"
    }

Parsing templates with repeated tokens
-----------------------------------------

If your template uses the same token more than once, then the library will handle it by adding an incremental digit to the token name when parsing and solving.

Here is an example of such a template being created.

.. code-block:: python

    import folderstructure as fs

    fs.add_token("project")
    fs.add_token(
        "division", development="DEV", art="ART", production="PROD", default="ART"
    )
    templates.add_template(
        'project_config',
        '//{project}/{division}/Pipe/{project}/{division}/CFG/config.json',
        anchor=fs.Template.ANCHOR_END
    )

    n.save_session()

When **Parsing** metadata using a template with repeated tokens, the dictionary you get back will have the keys for the repeated Token altered by an incremental digit at the end of the token name.

.. code-block:: python

    result = {
        "project1": "MyProject", "project2": "MyProject",
        "division1": "art", "division2": "production"
    }

There are many ways to substract that digit from the keys, but maybe the most reliable could be to use regular expressions. You can also use the ``folderstructure.get_token_options()`` and compare your keys to the pure Token option name.

.. code-block:: python

    import re

    pattern = re.compile(r'[a-zA-Z]+')
    for key in result.keys():
        print(pattern.search(key))

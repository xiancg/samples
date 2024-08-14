Folder Structure Repository
===============================

A repo for folderstructure consists of a series of JSON formated files (mainly: .token and .template, but also folderstructure.conf) that contain serialized Token and Template objects.

1. Repo location
------------------------

get_repo() will look in these places and with this priority to find a repo.

    1- ``force_repo`` Parameter passed when calling get_repo(force_repo), load_session(repo) or save_session(repo)

    2- Environment variable: FOLDERSTRUCTURE_REPO

    3- User config file: C:/Users/xxxxx/.NXATools/nxacore/config.json

    4- Dev config file: __file__/cfg/config.json

.. code-block:: python

    import folderstructure
    repo = folderstructure.get_repo()

2. Repo loading
------------------------

This will load all .token and .template files and create Python objects in memory to work with reading the repo location from locations 2 to 3 (Repo location section)

.. code-block:: python

    import folderstructure
    success = folderstructure.load_session()

3. Repo saving
------------------------
This will save all Token and Template objects in memory to serialized .token and .template files, as well as the name of the last active template in the folderstructure.conf file.

.. code-block:: python

    import folderstructure
    success = folderstructure.save_studio_core()

4. Repo creation
------------------------
Here is an example of creating a repository with a series of Tokens and Templates to solve and parse part of a folder structure.

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
        'project_dir',
        '{projects_root}/{project}',
        anchor=fs.Template.ANCHOR_END
    )
    fs.add_template(
        "division_root",
        '{@project_dir}/{division}',
        anchor=fs.Template.ANCHOR_END
    )
    fs.add_template(
        "project_config",
        '{@division_root}/PIPELINE/CFG/config.json',
        anchor=fs.Template.ANCHOR_END
    )
    fs.add_template(
        "asset_type",
        '{@division_root}/{asset_type}',
        anchor=fs.Template.ANCHOR_END
    )
    fs.add_template(
        "asset_root",
        '{@asset_type}/{asset}',
        anchor=fs.Template.ANCHOR_END
    )
    fs.add_template(
        "component_root",
        '{@asset_root}/{component}',
        anchor=fs.Template.ANCHOR_END
    )
    fs.add_template(
        "pipestep_vault",
        '{@division_root}/VAULT/{asset_type}/{asset}/{component}/Published/{pipeline_step}',
        anchor=fs.Template.ANCHOR_END
    )

    fs.set_active_template("project_config")

    fs.save_session()

This will result in the following files being created:

    - project_dir.template
    - project_config.template
    - division_root.template
    - asset_type.template
    - asset_root.template
    - component_root.template
    - pipestep_vault.template
    - folderstructure.conf
    - projects_root.token
    - project.token
    - division.token
    - asset_type.token
    - component.token

Let's dissect this code, block by block, to understand what's happening.

.. warning::
    It's important to manipulate both Tokens and Templates through the exposed package functions, not the object methods. This is so the system can keep track of what's created, removed, updated, etc during the repo session.

4.1. Adding Tokens
------------------------

.. code-block:: python
    :linenos:

    fs.add_token("projects_root")
    fs.add_token("division", DEV="DEV", ART="ART", PROD="PROD", default="ART")

In line 1 we're creating a **Required Token**. This means that for solving the user has to provide a value. This a explicit solve.

In line 2 we're creating an **Optional Token**, which means that for solving the user can pass one of the options in the Token or simply ignore passing a value and the Token will solve to it's default option. This is an implicit solve, which helps to greatly reduce the amount of info that needs to be passed to solve for certain cases.

For more information on implicit and explicit solving please check :doc:`solving`

4.2. Adding Templates
------------------------

.. code-block:: python
    :linenos:

    fs.add_template(
        'project_dir',
        '{projects_root}/{project}',
        anchor=fs.Template.ANCHOR_END
    )
    fs.add_template(
        "division_root",
        '{@project_dir}/{division}',
        anchor=fs.Template.ANCHOR_END
    )
    fs.add_template(
        "project_config",
        '{@division_root}/PIPELINE/CFG/config.json',
        anchor=fs.Template.ANCHOR_END
    )
    

Here we're creating templates, giving them a name, a pattern and an anchor respectively. *Name must be unique* for each template in the repo.

*Patterns* must be structured so that each Token is identified by it's name and enclosed between curly brackets '{ }'. Folder separators can be slashes or backslahes, but preferably slashes; the object will convert backslashes to slashes internally anyway.

You can **Reference** other Templates by using the **"@"** preceding the template name. The referenced template pattern will be expanded before parsing and solving. For example, if you want to solve for the 'project_config' template, you have to pass values for the 'projects_root', 'project' and 'division' tokens.

Since parsing uses regular expressions, *Anchors* are used to define where each template expects to find a match between the passed path and the pattern. Valid values are: Template.ANCHOR_START, Template.ANCHOR_END, Template.ANCHOR_BOTH

4.3. Active Template and saving session
-----------------------------------------

.. code-block:: python
    :linenos:

    fs.set_active_template("project_config")
    fs.save_session()

If there is only one template, it'll be set as active by default. If there is more than one, you need to activate that template before using parsing or solving.

When saving the session, all Tokens and Templates in memory will be saved to the repository along with a folderstructure.conf file that stores the last active Template (It'll be set as active again when loading the session from the repo next time.).

5. Repo manipulation from GUI
-----------------------------------------

We've implemented a PySide GUI to work with Folder Structure repos. From this dialog you can easily create and update repositories. It can run standalone or you can pass parent widget with a preset repo for use as part of the configuration of another tool.

Please check :doc:`Folder Strucutre GUI <gui>` for detailed info.
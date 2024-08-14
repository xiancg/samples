Solving
=====================

Solving from a Template means passing it some parameters and getting back a path to a file or directory.

.. note::
    The solving function is folderstructure.solve(args, kwargs)

Let's set these Tokens and Templates.

.. code-block:: python

    import folderstructure as fs

    # CREATE TOKENS
    fs.add_token("projects_root")
    fs.add_token("project")
    fs.add_token("division", DEV="DEV", ART="ART", PROD="PROD", default="DEV")

    # CREATE TEMPLATES
    fs.add_template(
        "project_config",
        '{projects_root}/{project}/{division}/PIPELINE/CFG/config.json',
        anchor=fs.Template.ANCHOR_END
    )

    fs.set_active_template("project_config")

Explicit Vs. Implicit
------------------------

It would not make any sense to make the user pass each and every Token all the time to be able to solve for a path. That'd be the equivalent, almost, to typing the path by hand. Also, it'd be good if the user doesn't have to know all token names by heart (though folderstructure.get_token_options() can help you with that).

That's why folderstructure.solve() accepts both args and kwargs. Not only that, but if given Token is optional and you want to use it's default value, you don't need to pass it at all.

.. code-block:: python

    fs.solve(projects_root="C:/Projects", project="MyProject", division="DEV")
    fs.solve(projects_root="C:/Projects", project="MyProject")
    fs.solve("C:/Projects", "MyProject", "DEV")
    fs.solve("C:/Projects", "MyProject")

Each of these calls to folderstructure.solve() will produce the exact same result:

.. note::
    C:/Projects/MyProject/ART/PIPELINE/CFG/config.json

If you don't pass a required Token (either as an argument or keyword argument), such as 'project' in this example, you'll get a TokenError.

Solving Templates with repeated tokens
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

When **Solving** a path for a template with repeated tokens you have three options:

1. Explicitly pass each repetition with an added digit for each repetition from left to right.

.. code-block:: python

    fs.solve(
        project1="MyProject_root", project2="MyProject2",
        division1="art", division2="production"
    )

2. Explicitly pass some of the repetitions with an added digit for each one. The ones you didn't pass are going to use the Token's default.

.. code-block:: python

    fs.solve(
        project1="MyProject_root", project2="MyProject2",
        division2="production"
    )

3. Explicitly pass just one argument, with no digit added. Your argument will be used for all token repetitions.

.. code-block:: python

    n.solve(
        project1="MyProject_root", project2="MyProject2",
        division="production"
    )
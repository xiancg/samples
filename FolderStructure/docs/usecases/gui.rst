Folder Structure - GUI
===============================

.. image:: /imgs/fs_gui.png
   :align: center
   :alt: Folder Structure GUI

We've implemented a PySide GUI to work with Folder Structure repos. From this dialog you can easily create and update repositories without writing a single line of code.

Standalone Vs Parented
-------------------------------
This gui can be executed in standalone mode like this:

.. code-block:: python

    from folderstructure.gui.launch import launch
    launch()

Or you can pass a parent widget with a preset repo to use it as part of the configuration of another tool:

.. code-block:: python

    from folderstructure.gui.launch import launch
    launch(repo_path="F:/MyFSRepo", parent=my_parent_widget_instance)


Templates
-------------------------------

.. image:: /imgs/fs_templates.png
   :align: center
   :alt: Templates

Templates are the rules the system follows to solve or parse any filepath. A Template is made of Tokens and hardcoded strings too. Right click on the list to see options available.

Template Pattern
-------------------------------

.. image:: /imgs/fs_templatepattern.png
   :align: center
   :alt: Template Pattern

This is how a Template pattern looks like. Values between *{ }* are Token placeholders. You can create Tokens in the second list and use them in any Template Pattern.

.. note::
    '{projects_root}/{project}/{division}/Pipe/CFG/config.json'

You can Reference other Templates by using the “@” preceding the template name. The referenced template pattern will be expanded before parsing and solving. For example, if you want to solve for the ‘project_config’ template, you have to pass values for the ‘projects_root’, ‘project’ and ‘division’ tokens in this case. What you see in the non-editable text box is the preview of your expanded pattern.

.. note::
    '{\@project_dir}/{division}/Pipe/CFG/config.json'

Templates have a special attribute called *Anchor*. This is how the regular expressions running behind scenes parse the paths, trying to analyze the path either from the start of the pattern, the end or both. A simple rule to keep in mind which option will work best, is that if you have a part of the pattern that's hardcoded, the anchor should be set to where that is. In the example above, it'd be a good idea to set the Anchor to *End*.

Tokens
-------------------------------

.. image:: /imgs/fs_tokens.png
   :align: center
   :alt: Tokens

Tokens are the meaningful parts of a Template. A Token can be **required**, meaning fully typed by the user, or can have a set of default options preconfigured. Right click on the list to see options available.

Token Options
-------------------------------

.. image:: /imgs/fs_tokenoptions.png
   :align: center
   :alt: Token Options

If Token is not required, then there has to be at least one option for it. If options are present, then one of them is the default one. Each option follows a *full_name:abbreviation* schema, so that paths can be short but meaning can be recovered easily. Right click on the list to see options available.
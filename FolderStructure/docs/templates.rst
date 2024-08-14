Templates Module
================================

Templates are the rules the system follows to solve or parse any filepath. A Template is made of Tokens and hardcoded strings too. This is how a Template pattern looks like. Values between *{ }* are Token placeholders.

.. note::
    '{projects_root}/{project}/{division}/Pipe/CFG/config.json'

You can Reference other Templates by using the “@” preceding the template name. The referenced template pattern will be expanded before parsing and solving. For example, if you want to solve for the ‘project_config’ template, you have to pass values for the ‘projects_root’, ‘project’ and ‘division’ tokens.

.. note::
    '{\@project_dir}/{division}/Pipe/CFG/config.json'

Templates have a special attribute called *Anchor*. This is how the regular expressions running behind scenes parse the paths, trying to analyze the data either form the start of the pattern, the end or both. A simple rule to keep in mind which option will work best, is that if you have a part of the pattern that's hardcoded, the anchor should be set to where that is.

.. automodule:: folderstructure.templates
   :noindex:
   :members:
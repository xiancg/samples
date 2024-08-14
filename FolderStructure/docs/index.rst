Folder Structure Documentation
===========================================

Folder Structure is our utility to **SOLVE** and **PARSE** file system locations. Solving means constructing a file or folder path from given parameters. Parsing means taking a path and extracting metadata from it (Folder and file names have parts with specific meanings that we can use).

Installation
-----------------

.. code-block::

    pip install folderstructure --index-url https://pypi.collidercraftworks.com/simple --trusted-host pypi.collidercraftworks.com


General Ideas
-----------------

Folder Structure consists of two main entities: ``Token`` and ``Template``. Both of them are written and read to and from a *repository* that contains their serialized versions.

A Template is made of Tokens and hardcoded strings too. This is how a Template pattern looks like. Values between curly braces '{ }' are Token placeholders. 

.. note::
    '{projects_root}/{project}/{division}/Pipe/CFG/config.json'

Behind scenes Folder Structure uses regular expressions to solve and parse. The logic is largely based on *Martin's Pengelly-Phillips Lucidity*, but adapted to work with our repo and serialization methods and implicit and explicit solving. Also, since Lucidity hasn't got any updates for a long time, we decided to make our own thing.

Folder Structure - GUI
------------------------

.. image:: /imgs/fs_gui.png
   :align: center
   :alt: Folder Structure GUI

We've implemented a PySide GUI to work with Folder Structure repos. From this dialog you can easily create and update repositories without writing a single line of code. Please refer to :doc:`usecases/gui` for more details.


folderstructure package
------------------------
``folderstructure`` is the package of **Folder Structure**. Please refer to :doc:`folderstructure` for further details.

It consists of two key functions:

    1. parse(path)
    2. solve(args, kwargs)

And three working functions:

    1. get_repo()
    2. load_session()
    3. save_session()

To load serialized Tokens and Templates from repo.

.. code-block:: python

    import folderstructure
    repo = folderstructure.get_repo()
    success = folderstructure.load_session(repo)

To save serialized Tokens and Templates to repo.

.. code-block:: python

    import folderstructure
    repo = folderstructure.get_repo()
    success = folderstructure.save_session(repo)


logger module
--------------------
``folderstructure.logger`` uses Python logging to track almost everything that's happening under the hood. This is really useful for debugging. Please refer to :doc:`logger` for further details.

This is going to initialize the logger and output to stdout (console, terminal, etc)

.. code-block:: python

    import folderstructure
    folderstructure.logger.init_logger()

This is going to initalize a log file where everything will be recorded.

.. code-block:: python

    import folderstructure
    folderstructure.logger.init_file_logger()


.. toctree::
   :maxdepth: 4
   :caption: Getting Started

   usecases/repocreation
   usecases/solving
   usecases/parsing
   usecases/gui

.. toctree::
   :maxdepth: 4
   :caption: Reference

   tokens
   templates

.. toctree::
   :maxdepth: 3
   :caption: Changelog and Roadmap

   changelog
   roadmap

Getting Started
=========================================

The Sanity Checker is a framework library which means that it is expected to be used by developers to implement their own checks for their needs. Its main goal is to be easily extended with new checks and to provide a simple and reliable way to run them for the users.

Repositories
-----------------
The library uses the idea of repositories to work with checks. A repository is a folder that contains a set of checks. The library will look for SanityChecks and SharedContexts in a set of given paths and will load instances of all the checks and contexts found in them. The library supports the use of multiple repositories at the same time. This allows to have a set of checks that are common to all projects and a set of checks that are specific to a project for example.

.. image:: /imgs/repo.png
   :align: center
   :alt: Repository

You may structure the repo and Python modules as you wish. The framework only cares about the classes that inherit from the base ``SanityCheck`` and ``SharedContext``.

Core entities
-----------------
Sanity Checker uses two main entities from which check developers must inherit from and use as a basis: ``SanityCheck`` and ``SharedContext``. A ``SanityCheck`` is a class that implements a check. A ``SharedContext`` is a class that implements a context that can be shared between checks (i.e.: A merged mesh).

Status management
--------------------
Already composited on the core classes from the constructor, Sanity Checker also provides a ``CheckStatus`` and ``ContextStatus`` classes that must be used to report the status of a check or context. You don't need to reimplement these yourself, you just need to use the given instance that base classes provide already. These are used by the GUI to display the status of the checks and custom messages for the user. Every time you change either the ``status.code`` or the ``status.message`` the GUI is refreshed with those changes.

Actions
--------------------
Optionally, the developer can also implement the ``Action`` class and register it with any check. This class is used to provide optional actions the user can execute to help in the resolution of the check. For example, an action to open the folder where a file is supposed to be.

Registries
--------------------
The framework maintains a register of all loaded checks and contexts in memory.

.. note::
   **PRO TIP:** Use the Reload button in the GUI to iterate a lot quicker on your checks development. It'll wipe out these registers and reload everything with your updated changes.

Presets
---------------------------
You can setup a ``presets.json`` file in your repo root following the structure of the next example to create presets the user will be able to take advantage of from the GUI.

.. image:: /imgs/presets.png
   :align: center
   :alt: Presets

.. code-block:: python

   {
      "Quick check":[
         "MyAwesomeCheck1",
         "MyAwesomeCheck3",
         "MyAwesomeCheck5",
         "MyAwesomeCheck7",
         "MyAwesomeCheck9"
      ],
      "UVs":[
         "SarasaContext",
         "MyAwesomeCheck2",
         "MyAwesomeCheck4",
         "MyAwesomeCheck6",
         "MyAwesomeCheck8"
      ]
   }

Progress
---------------------------
Each SanityCheck and SharedContext comes with a ``ProgressInterface`` instance. If found and used, the GUI will show a small progress bar for each check and context while it runs.

.. code-block:: python

   import sanitychecker as sc

   class TestCheck(sc.SanityCheck):
      def __init__(self):
         super(TestCheck, self).__init__()
      
      def _check(self):
         self.progress.reset_progress()
         self.progress.maximum = 36
         for i in range(36):
            self.progress.add_progress()
            time.sleep(0.1)
         self.progress.reset_progress()

         return self.status

Logging
---------------------------

.. code-block:: python

   from sanitychecker import logger, logger_gui

``logger`` will log to ``stdout`` (console, script editor, output window) and if **Log to File** is activaded in the GUI it will also save a .log file. ``logger_gui`` will log to the GUI only. All ``logger_gui`` messages propagate to ``logger`` by default.

The framework uses only the lowest logging level (DEBUG) to log its messages.

This means that you can use the rest of the levels to log your own messages for the user (INFO, WARNING, ERROR, CRITICAL).

A logging level can be setup by the user at any time from the GUI.

.. image:: /imgs/logging.png
   :align: center
   :alt: Logging

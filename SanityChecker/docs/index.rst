Sanity Checker Documentation
=========================================

Sanity Checker is a framework to create, manage and run sanity tests for any project or workflow in the production pipeline. The framework is designed to be agnostic of checks requirements and implementation. Its main goal is to be easily extended with new checks and to provide a simple and reliable way to run them.

Installation
-----------------

.. code-block::

    pip install sanitychecker --index-url https://pypi.collidercraftworks.com/simple --trusted-host pypi.collidercraftworks.com

General Ideas
-----------------

The framework is composed of two main parts: the Sanity Checker library and the Sanity Checker GUI. The library is the core of the framework and it is responsible for managing the checks and running them. The GUI is a PySide app that provides an interface for end users to run them.

Sanity Checker - GUI
------------------------

.. image:: /imgs/sc_gui.png
   :align: center
   :alt: Sanity Checker GUI

We've implemented a PySide GUI to work with Sanity Checker repos. The GUI allows the user run checks and see the results. It can also be a useful tool for developers to iterate over checks by using the reload functionality which will reload all the checks and contexts from the repositories.

To use the GUI as a standalone app run the following command after installing the package in your interpreter:

.. code-block:: python

    import sanitychecker as sc
    repos = ["C:/path/to/repo1", "C:/path/to/repo2"]
    sc.launch_standalone(repos)

To use the GUI inside Maya run the following command:

.. code-block:: python

    import sanitychecker as sc
    repos = ["C:/path/to/repo1", "C:/path/to/repo2"]
    sc.launch_maya(repos)


.. toctree::
   :maxdepth: 4
   :hidden:
   :caption: For Artists

   forartists/gettingstarted
   forartists/checks
   forartists/contexts

.. toctree::
   :maxdepth: 4
   :hidden:
   :caption: For Developers

   fordevs/gettingstarted
   fordevs/implementingchecks
   fordevs/usingcontexts

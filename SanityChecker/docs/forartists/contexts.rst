Contexts
=========================================

Sometimes a certain setup is needed for a number of checks to execute. For example: A merged mesh of a character, a headless instance of Maya, etc. This is where contexts come in handy. You see this context-checks relationship in the hierarchy structure of checks in the GUI.

.. image:: /imgs/context_hierarchy.png
   :align: center
   :alt: Contexts and checks hierarchy

Checks that are not below a context, are completely independent and can be executed with their own setup or with no setup at all.

Setup and Teardown
--------------------
If you want to execute a context setup, you can simply click on its *Setup* button. Remember to run the *Teardown* option when you're done.

.. note::
    If you run an individual check that relies on a context, the check itself will run the context setup and teardown automatically, you don't need to do it yourself.
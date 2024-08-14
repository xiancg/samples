Using SharedContexts
=========================================

Sometimes a certain setup is needed for a number of checks to execute. For example: A merged mesh of a character, a headless instance of Maya, etc. This is where contexts come in handy. You see this context-checks relationship as a hierarchy structure of checks in the GUI.

.. image:: /imgs/context_hierarchy.png
   :align: center
   :alt: Contexts and checks hierarchy

Checks that are not below a context, are completely independent and can be executed with their own setup or with no setup at all.

The only hard requirement of a SharedContext is that you need to reimplement the ``_setup()`` method and return a status from it. A normal implementation of a SharedContext will look like this:

.. code-block:: python

    import sanitychecker as sc
    class MergeContext(sc.SharedContext):
        def __init__(self):
            super(MergeContext, self).__init__()

        def _setup(self):
            # Do your setup here
            self.status.code = sc.ContextStatus.ready
            self.status.message = "Mesh merge ready"

            return self.status

        def _teardown(self):
            self.status.code = sc.ContextStatus.finished
            self.status.message = "Mesh merge removed"
            return self.status

Setup and Teardown
--------------------
If the user runs an individual check that relies on a context, the check itself will run the context setup and teardown automatically, you don't need to implement anything additional.
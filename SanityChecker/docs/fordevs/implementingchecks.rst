Implementing SanityCheck
=========================================

The only hard requirement of a SanityCheck is that you need to reimplement the ``_check()`` method and return a status from it. A bare bones implementation of a SanityCheck will look like this:

.. code-block:: python

    import sanitychecker as sc

    class TestCheck(sc.SanityCheck):
        def __init__(self):
            super(TestCheck, self).__init__()

        def _check(self):
            self.status.code = sc.CheckStatus.passed
            self.status.message = "Hello World!"
            return self.status

Full check flow
-----------------

    1. Setup (optional)
    2. Check 
    3. Fix (optional)
    4. Check fix (optional)
    5. Teardown (optional)

Other than the ``_check()`` method itself, you may also implement a ``_fix()`` method that the framework will try to use if your check fails for the end user.

Each check may also have its own ``_setup()`` and ``_teardown()`` methods. Sometimes a certain setup is needed for a particular check to execute (i.e.: A headless instance of Houdini). This is where setup and teardown come in handy. The framework will call the ``_setup()`` method before executing the check and the ``_teardown()`` method after the check has been executed. This is also useful for cleaning up any resources that might have been created during the check execution.

.. code-block:: python

    class TestCheck(sc.SanityCheck):
        def __init__(self):
            super(TestCheck, self).__init__()

        def _check(self):
            self.status.code = sc.CheckStatus.passed
            self.status.message = "Hello World!"
            return self.status
        
        def _fix(self):
            self.status.message = "I'm being fixed!"
            return self.status

        def _setup(self):
            self.status.message = "I'm getting ready!"
            return self.status

        def _teardown(self):
            self.status.message = "You're killing me!"
            return self.status

SanityCheck properties
---------------------------
In the class constructor you can define a number of properties that will be used by the framework if defined.

.. code-block:: python

    class TestCheck(sc.SanityCheck):
        def __init__(self):
            super(TestCheck, self).__init__()
            self.name = "My awesome check"
            self.description = "Checks for awesomeness"
            self.priority = 27
            self.shared_context = "MergeContext"
            self.denpendencies_names = ["AnotherCheck", "YetAnotherCheck"]

Optional actions
---------------------------
Additionaly, you can give the user tools he/she can execute at any time and that might help with, let's say, a manual fix of the check at hand (i.e.: Select Vertices, Select Head, etc). Use the ``register_actions()`` method in the constructor to initialize them.

.. code-block:: python

    import sanitychecker as sc

    class MyAwesomeAction(sc.Action):
        def __init__(self):
            super(MyAwesomeAction, self).__init__()
            self.name = "My awesome action"
            self.description = "This is my awesome action"
        
        def _execute(self):
            print("I'm doing something awesome!")

    class TestCheck(sc.SanityCheck):
        def __init__(self):
            super(TestCheck, self).__init__()
            self.register_actions([MyAwesomeAction()])

Getting Started
=========================================

By default the tool will launch with all the preset configuration of checks the developer set for you, so you don't really need to know anything other than just click on Run Checks and wait for the results!

.. image:: /imgs/runchecks.png
   :align: center
   :alt: Run Checks

Presets
-----------------
You may use the presets to quickly change the configuration of checks. These are provided by the developers of each checks repo.

.. image:: /imgs/presets.png
   :align: center
   :alt: Presets

Wanna know more
-----------------
If you're curious, here is what the tool does when you click on Run Checks:

**Checks that rely on a Shared Context**

    1. Setup the context for you. For example: merge all the meshes of a character into one mesh.
    
    2. Run all checks.
    
    3. Teardown the context. For example: eliminate the merged mesh and restore any change made in setup.


**Checks that do not rely on a Shared Context**

    1. Run all checks.

.. note::
    Please keep in mind that if the developer has provided a possible Fix for a failed check, the tool will try to run that Fix for you and then run the check again. So you don't really need to run it manually.

And that's it! You can now start using the tool to check your assets. If you're more of a control freak, please refer to the next section: :doc:`checks` and :doc:`contexts`
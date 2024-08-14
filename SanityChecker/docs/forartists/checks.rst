Sanity Checks
=========================================

All Sanity Checks developed and loaded in the tool have at the very least a Check implementation. You can run individual checks by using the Check button on each check.

.. image:: /imgs/checkslist.png
   :align: center
   :alt: Checks list

Full check flow
-----------------
    1. Setup (optional)
    2. Check 
    3. Fix (optional)
    4. Check fix (optional)
    5. Teardown (optional)

*Optional* means that developers can choose to implement these methods or not and they will show up in the tool as buttons only if implemented. You can run each step independently by using these buttons. This gives you fine grain control over each check and allows you to debug them to your heart's content.

Run check only
-----------------
Please keep in mind that Left Clicking on the Check button will run the *Full check flow* mentioned above. If you Right Click on the Check button you'll see the option to run only the check method.

.. image:: /imgs/check_rightclick.png
   :align: center
   :alt: Check Right Click

Optional Actions
-----------------
Additionally, the developer can provide *Optional Actions* you can run at any time, that facilitate certain operations you might need for manual fixes for example. If implemented, you'll find them right next to the Check buttons as their own little button per action implemented.

Dependencies
-----------------
A developer can also establish if a check needs other checks to happen and pass first before even trying to run the current check. This is a performance optimization mostly. Sometimes you don't want to run a heavy load check if a previous check already failed. If configured, you'll see these dependencies listed bellow the check description.
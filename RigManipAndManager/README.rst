Rig Manipulator and Manager - (Maya C++ API, Python, PySide)
--------------------------------------------------------------

The Rig Manager is a dockable PySide GUI to facilitate selection and manipulation of facial rigs in a scene. It mimics selection behavior of Maya and features a set of selection operations like box drag, radial drag, proximity selection, selection mirroring, region selection, etc. It's data backend is supported by a custom ORM that maps the rig data to a SQLite database where all control relationships, default values and other rig data is stored.

.. image:: face_regions.gif
   :alt: Rig Manager - Face regions
   :align: center

.. image:: layers.png
   :alt: Rig Manager - Layers
   :align: center

As a companion to the Rig Manager, I also wrote a Rig Manipulator which is a Maya plugin that creates a tool (a context in Maya's API terms) to let the user select and move the facial rig controls with the same tool (without having to switch from selection to move tool). The manipulator is also aware of the selection operations performed in the Rig Manager and the SQLite database, so it can be used to work with the controls in the same way through key modifiers and mouse buttons combinations.

.. image:: rigmanipulator.gif
   :alt: Rig Manipulator
   :align: center

Only relevant parts of the code are shown here.
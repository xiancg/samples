Folder Structure - (Python, PySide)
--------------------------------------------------------------

Folder Structure is a library I wrote to **SOLVE** and **PARSE** file system locations. Solving means constructing a file or folder path from given parameters. Parsing means taking a path and extracting metadata from it (Folder and file names have parts with specific meanings that we can use).

It features serializable entities called ``Token`` and ``Template``. Both of them are written and read to and from a *repository* that contains their serialized versions.

This library is hosted in a private Python Packages Index (PyPI) repository with LDAP which I setup for my team.
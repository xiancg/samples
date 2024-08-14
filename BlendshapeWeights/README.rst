Blendshape Weights IO (Maya C++ API)
======================================

This is a Maya C++ plugin for import/export of blendshape target per vertex weights to a custom binary file format. It is used to help in the setup and automation of complex mixing of other deformers. It's first implementation was as part of the dismemberment transfer automation workflow I developed for Mortal Kombat, which included a batch processing standalone GUI application that connected to Perforce leveraging QThreads and used Maya in headless mode to process all the work.

Only relevant parts of the code are shown here, with permission from the owners.
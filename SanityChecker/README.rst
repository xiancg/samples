Sanity Checker - (Python, PySide)
--------------------------------------------------------------

Sanity Checker is a framework to create, manage and run sanity tests for any project or workflow in the production pipeline. The framework is designed to be agnostic of checks requirements and implementation. Its main goal is to be easily extended with new checks and to provide a simple and reliable way to run them.

The library uses the idea of repositories to work with checks. A repository is a folder that contains a set of checks. The library will look for SanityChecks and SharedContexts in a set of given paths and will load instances of all the checks and contexts found in them. The library supports the use of multiple repositories at the same time. This allows to have a set of checks that are common to all projects and a set of checks that are specific to a project for example.

This library is hosted in a private Python Packages Index (PyPI) repository with LDAP which I setup for my team.

Only relevant parts of the code are shown here.
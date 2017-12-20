Package ``f311`` API
====================

The *collaboration model*
-------------------------

Package ``f311`` provides a plugin-like model (*collaboration model*)
that allows 3rd-party *collaborator packages* to contribute with:

- ``f311.DataFile`` subclasses, *i.e.*, implement handling (load, save, etc.) of new file types;
- ``f311.Vis`` subclasses, *i.e.*, implement visualizations for these files;
- Standalone scripts that will be listed by ``programs.py``

Creating a collaborator project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Start your new project. A template project skeleton is available with the source code as a
   directory named ``template-project``;
2. Create new resources as listed above;
3. In order to make package `f311` "see" the new project, create a pull request for project
   F311 on GitHub (https://github.com/trevisanj/f311), and append your package name to
   the `f311.collaboration.EXTERNAL_COLLABORATORS` list.


The file handling API
---------------------

All file handling classes descend from :any:`DataFile`, containing some basic methods:

- ``load()``: loads file from disk into internal object variables
- ``save_as()``: saves file to disk
- ``init_default()``: initializes file object with default information

.. todo:: expand
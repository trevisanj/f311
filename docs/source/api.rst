Collaboration
=============

The *collaboration model*
-------------------------

Package ``f311`` provides a plugin-like model (*collaboration model*)
that allows 3rd-party *collaborator packages* to contribute with:

- ``f311.DataFile`` subclasses
- ``f311.Vis`` subclasses
- Standalone scripts

Implications
------------

- New file types are recognized in the F311 API, *e.g.* using methods ``f311.load_any_file()``, ``f311.load_spectrum()``,
  ``f311.tabulate_filetypes_rest()``
- New file types and their visualizations are recognized in ``explorer.py``
- Scripts will be indexed by ``programs.py``

Creating a collaborator project
-------------------------------

1. Start your new project. A template project skeleton is available with the source code as a
   directory named ``template-project``
2. Create new resources as listed in the beginning of this section;
3. In order to make package `f311` "see" the new project, create a pull request for project
   F311 on GitHub (https://github.com/trevisanj/f311), and append your package name to
   the `f311.collaboration.EXTERNAL_COLLABORATORS` list.


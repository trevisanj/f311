.. code-block:: none

    usage: programs.py [-h] [-p PKGNAME] [-l] [-k] [-_]
                       [{text,markdown-list,markdown-table,rest-list,rest-toctree}]
    
    Lists all programs available
    
    positional arguments:
      {text,markdown-list,markdown-table,rest-list,rest-toctree}
                            Print format (default: text)
    
    optional arguments:
      -h, --help            show this help message and exit
      -p PKGNAME, --pkgname PKGNAME
                            List programs from this package only (default: (all))
      -l, --list-packages   Lists all packages (default: False)
      -k, --rest-links      If format=="rest-list", renders program names as links
                            to their respective documentation pages (default:
                            False)
      -_, --protected       Includes protected scripts (starting with '_')_
                            (default: False)
    

This script belongs to package *f311*

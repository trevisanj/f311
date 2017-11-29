.. code-block:: none

    usage: copy-star.py [-h] [-l] [-p] [directory]
    
    Copies stellar data files (such as main.dat, abonds.dat, dissoc.dat) to local directory
    
    examples of usage:
      > copy-star.py
      (displays menu)
    
      > copy-star.py arcturus
      ("arcturus" is the name of a subdirectory of PFANT/data)
    
      > copy-star.py -p /home/user/pfant-common-data
      (use option "-p" to specify path)
    
      > copy-star.py -l
      (lists subdirectories of PFANT/data , doesn't copy anything)
    
    positional arguments:
      directory   name of directory (either a subdirectory of PFANT/data or the
                  path to a valid system directory (see modes of operation)
                  (default: None)
    
    optional arguments:
      -h, --help  show this help message and exit
      -l, --list  lists subdirectories of
                  /home/j/Documents/projects/astro/github/PFANT/code/data
                  (default: False)
      -p, --path  system path mode (default: False)
    

This script belongs to package *f311.pyfant*

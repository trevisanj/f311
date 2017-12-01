.. code-block:: none

    usage: organize-directory.py [-h]
    
    Organizes simulation directory (creates folders, moves files, creates 'index.html')
    
      - moves 'root/report-*'       to 'root/reports'
      - moves 'root/C*'             to 'root/raw'
      - moves 'root/raw/simgroup*'  to 'root/'
      - moves 'root/raw/report-*'   to 'root/reports'
      - moves 'root/raw/group*.splist'   to 'root'
      - [re]creates 'root/reports/index.html'
    
    This script can be run from one of these directories:
      - 'root' -- a directory containing at least one of these directories: 'reports', 'raw'
      - 'root/raw'
      - 'root/reports'
    
    The script will use some rules to try to figure out where it is running from
    
    optional arguments:
      -h, --help  show this help message and exit
    

This script belongs to package *f311.aosss*

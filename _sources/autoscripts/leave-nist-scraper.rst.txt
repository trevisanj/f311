.. code-block:: none

    usage: nist-scraper.py [-h] formula
    
    Retrieves and prints a table of molecular constants from the NIST Chemistry Web Book [NISTRef]
    
    To do so, it uses web scraping to navigate through several pages and parse the desired information
    from the book web pages.
    
    It does not provide a way to list the molecules yet, but will give an error if the molecule is not
    found in the NIST web book.
    
    Example:
    
        print-nist.py OH
    
    **Note** This script was designed to work with **diatomic molecules** and may not work with other
             molecules.
    
    **Warning** The source material online was known to contain mistakes (such as an underscore instead
                of a minus signal to indicate a negative number). We have identified a few of these,
                and build some workarounds. However, we recommend a close look at the information parsed
                before use.
    
    **Disclaimer** This script may stop working if the NIST people update the Chemistry Web Book.
    
    References:
    
    [NISTRef] http://webbook.nist.gov/chemistry/
    
    positional arguments:
      formula     NIST formula
    
    optional arguments:
      -h, --help  show this help message and exit
    

This script belongs to package *f311.convmol*

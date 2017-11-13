.. code-block:: none

    usage: hitran-scraper.py [-h] [-t T] [M] [I] [llzero] [llfin]
    
    Retrieves molecular lines from the HITRAN database [Gordon2016]
    
    This script uses web scraping and the HAPI to save locally molecular lines from the HITRAN database.
    
    While the HAPI provides the downloading facility, web scraping is used to get the lists of molecules
    and isotopologues from the HITRAN webpages and get the IDs required to run the HAPI query.
    
    The script is typically invoked several times, each time with an additional argument.
    
    References:
    
    [Gordon2016] I.E. Gordon, L.S. Rothman, C. Hill, R.V. Kochanov, Y. Tan, P.F. Bernath, M. Birk,
        V. Boudon, A. Campargue, K.V. Chance, B.J. Drouin, J.-M. Flaud, R.R. Gamache, J.T. Hodges,
        D. Jacquemart, V.I. Perevalov, A. Perrin, K.P. Shine, M.-A.H. Smith, J. Tennyson, G.C. Toon,
        H. Tran, V.G. Tyuterev, A. Barbe, A.G. Császár, V.M. Devi, T. Furtenbacher, J.J. Harrison,
        J.-M. Hartmann, A. Jolly, T.J. Johnson, T. Karman, I. Kleiner, A.A. Kyuberis, J. Loos,
        O.M. Lyulin, S.T. Massie, S.N. Mikhailenko, N. Moazzen-Ahmadi, H.S.P. Müller, O.V. Naumenko,
        A.V. Nikitin, O.L. Polyansky, M. Rey, M. Rotger, S.W. Sharpe, K. Sung, E. Starikova,
        S.A. Tashkun, J. Vander Auwera, G. Wagner, J. Wilzewski, P. Wcisło, S. Yu, E.J. Zak,
        The HITRAN2016 Molecular Spectroscopic Database, J. Quant. Spectrosc. Radiat. Transf. (2017).
        doi:10.1016/j.jqsrt.2017.06.038.
    
    positional arguments:
      M           HITRAN molecule number (default: (lists molecules))
      I           HITRAN isotopologue number (not unique, starts over at each
                  molecule) (default: (lists isotopologues))
      llzero      Initial wavelength (Angstrom) (default: None)
      llfin       Final wavelength (Angstrom) (default: None)
    
    optional arguments:
      -h, --help  show this help message and exit
      -t T        Table Name (default: (molecular formula))
    

This script belongs to package *f311.convmol*

NIST Scraper
============

``nist-scraper.py`` retrieves and prints a table of molecular constants from the

NIST Chemistry Web Book for a particular molecule.

To do so, it uses web scraping to navigate through several pages and parse the desired information
from the book web pages.

It does not provide a way to list the molecules yet, but will give an error if the molecule is not
found in the NIST web book.

.. note:: This script was designed to work with **diatomic molecules** and may not work with other
          molecules.

.. warning:: The source material online was known to contain mistakes (such as an underscore instead of a minus
             signal to indicate a negative number). We have identified a few of these, and build
             some workarounds. However, we recommend a close look at the information parsed
             before use.

Usage examples:

.. code:: shell

    nist-scraper.py TiO

::

    *** titanium oxide ***

    State       T_e            omega_e    omega_ex_e    omega_ey_e      B_e    alpha_e    gamma_e       D_e    beta_e      r_e  Trans.       nu_00
    ----------  -----------  ---------  ------------  ------------  -------  ---------  ---------  --------  --------  -------  --------  --------
    D           31920.0        1040                                                                                             D ? X     31940
    e ?Sigma?   a + 26598.1     845.2          4.2                  0.4892     0.0023              4.7e-07             1.695    e ? d R   24297.5
    f ?Delta    (a + 19132)     890                                 0.50221                        6.4e-07             1.67292  f ? a R   19068.9
    c ?Phi      a + 17890.2     909.6          4.19                 0.523      0.00313             3.9e-07             1.6393   c ? a R   17840.6
    C ³Delta_r  19617.0         838.26         4.76         0.047   0.48989    0.00306   -3e-05    6.7e-07             1.69383  C ? X R   19334
    B ³Pi_r     16331.3         875            5                    0.50617                        6.86e-07            1.66636  B ? X R   16066.7
    b ?Pi       a+11322.0_3     911.2          3.72                 0.51337    0.00291             6.1e-07             1.65464  b ? d R    9054.02
    A ³Phi_r    14431.0         867.78         3.942                0.50739    0.00315   -1e-05    6.92e-07     2e-09  1.66436  A ? X R   14163
    E ³Pi       12025.0         924.2          5.1                                                                              E ? X     11871
    d ?Sigma?   a + 2215.6     1014.6          4.64                 0.54922    0.00337             6e-07               1.59972
    a ?Delta    a              1009.3          3.93                 0.5376     0.00298             5.9e-07             1.61692
    X ³Delta_r  197.5          1009.02         4.498       -0.0107  0.53541    0.00301   -1.1e-05  6.03e-07     3e-09  1.62022

.. code:: shell

    nist-scraper.py OH

::

    *** Hydroxyl radical ***

    State          T_e    omega_e    omega_ex_e  omega_ey_e        B_e    alpha_e    gamma_e       D_e  beta_e        r_e  Trans.        nu_00
    ---------  -------  ---------  ------------  ------------  -------  ---------  ---------  --------  --------  -------  ---------  --------
    C ²Sigma?  89459.1    1232.9        19.1                    4.247      0.078              0.0002              2.0461   C ? A R    55820.7
    C ²Sigma?                                                                                                              (C ? X)    88223
    D ²Sigma?  82130      2954                                 15.2179                        0.001616            1.08093  D ? X R    81759.8
    B ²Sigma?  69774       660                                  5.086                         0.000929            1.8698   B ? A R    35965.5
    A ²Sigma?  32684.1    3178.86       92.917                 17.358      0.7868     -0.016  0.002039            1.0121   A ? X R    32402.4
    X ²Pi_i        0      3737.76       84.8813                18.9108     0.7242             0.001938            0.96966  1/2 ? 3/2    126.23

HITRAN Scraper
==============

``hitran-scraper.py`` uses `web scraping <https://en.wikipedia.org/wiki/Web_scraping>`
and the `HAPI <http://hitran.org/hapi>` to save locally molecular lines from the HITRAN database.

While the HAPI provides the downloading facility, web scraping is used to get the lists of molecules
and isotopologues from the HITRAN webpages and get the IDs required to run the HAPI query.

The script is typically invoked several times, each time with an additional argument:

.. code:: shell

    $ hitran-scraper.py

    List of all HITRAN molecules
    ============================

      ID  Formula    Name
    ----  ---------  --------------------
       1  H2O        Water
       2  CO2        Carbon Dioxide
       3  O3         Ozone
       4  N2O        Nitrous Oxide
       5  CO         Carbon Monoxide
       6  CH4        Methane
       7  O2         Molecular Oxygen
       8  NO         Nitric Oxide
       9  SO2        Sulfur Dioxide
      10  NO2        Nitrogen Dioxide
      11  NH3        Ammonia
      12  HNO3       Nitric Acid
      13  OH         Hydroxyl Radical
      14  HF         Hydrogen Fluoride
      15  HCl        Hydrogen Chloride
      16  HBr        Hydrogen Bromide
      17  HI         Hydrogen Iodide
      18  ClO        Chlorine Monoxide
      19  OCS        Carbonyl Sulfide
      20  H2CO       Formaldehyde
      21  HOCl       Hypochlorous Acid
      22  N2         Molecular Nitrogen
      23  HCN        Hydrogen Cyanide
      24  CH3Cl      Methyl Chloride
      25  H2O2       Hydrogen Peroxide
      26  C2H2       Acetylene
      27  C2H6       Ethane
      28  PH3        Phosphine
      29  COF2       Carbonyl Fluoride
      31  H2S        Hydrogen Sulfide
      32  HCOOH      Formic Acid
      33  HO2        Hydroperoxyl Radical
      34  O          Oxygen Atom
      36  NO+        Nitric Oxide Cation
      37  HOBr       Hypobromous Acid
      38  C2H4       Ethylene
      39  CH3OH      Methanol
      40  CH3Br      Methyl Bromide
      41  CH3CN      Methyl Cyanide
      43  C4H2       Diacetylene
      44  HC3N       Cyanoacetylene
      45  H2         Molecular Hydrogen
      46  CS         Carbon Monosulfide
      47  SO3        Sulfur trioxide

    Now, to list isotopologues for a given molecule, please type:

        hitran-scraper.py <molecule ID>

    where <molecule ID> is one of the IDs listed above.

Now suppose we want the molecule OH molecule:

.. code:: shell

    $ hitran-scraper.py 13

    List of all isotopologues for molecule 'OH' (Hydroxyl Radical)
    ==============================================================

    m_formula      ID    ID_molecule  Formula      AFGL_Code  Abundance
    -----------  ----  -------------  ---------  -----------  ---------------
    OH              1             13  (16)OH              61  0.997473
    OH              2             13  (18)OH              81  0.002
    OH              3             13  (16)OD              62  1.553710 × 10-4

    Now, to download lines, please type:

        hitran-scraper.py 13 <isotopologue ID> <llzero> <llfin>

    where <isotopologue ID> is one the numbers from the 'ID' column above,

    and [<llzero>, <llfin>] defines the wavelength interval in Angstrom.

Now selecting the first isotopologue and specifying the visible wavelength range:

.. code:: shell

    $ hitran-scraper.py 13 1 3000 7000

    Isotopologue selected:
    ======================

    Field name    Value
    ------------  --------
    m_formula     OH
    ID            1
    ID_molecule   13
    Formula       (16)OH
    AFGL_Code     61
    Abundance     0.997473

    Wavelength interval (air): [3000.0, 7000.0] Angstrom
    Wavenumber interval (vacuum): [14289.61969369552, 33342.42546386186] cm**-1
    Table name: '(16)OH'

    Fetching data...
    ===
    === BEGIN messages from HITRAN API ===
    ===
    BEGIN DOWNLOAD: (16)OH
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
      65536 bytes written to ./(16)OH.data
    Header written to ./(16)OH.header
    END DOWNLOAD
                         Lines parsed: 3855
    PROCESSED
    ===
    === END messages from HITRAN API ===
    ===
    ...done
    Please check files '(16)OH.header', '(16)OH.data'

**Hint** The files created ('(16)OH.header', '(16)OH.data') can be opened using the `HAPI <http://hitran.org/hapi>`.
They are also accessed by the application ``convmol.py``.

The HAPI can be downloaded, but one version is also included with the f311 package. The following
is an example of how the HITRAN data could be accessed from the Python console:

>>> from f311 import hapi
>>> hapi.loadCache()
Using .
(16)OH
                     Lines parsed: 3855
>>> oh_data = hapi.LOCAL_TABLE_CACHE["(16)OH"]
>>> oh_data.keys()
dict_keys(['data', 'header'])
>>> oh_data["data"].keys()
dict_keys(['ierr', 'gpp', 'molec_id', 'global_lower_quanta', 'sw', 'gamma_self', 'n_air', 'elower', 'line_mixing_flag', 'local_lower_quanta', 'gp', 'global_upper_quanta', 'gamma_air', 'local_upper_quanta', 'iref', 'local_iso_id', 'delta_air', 'nu', 'a'])

To work properly with these data, you should have a look at the HAPI source code and manual, as this library is
superbly documented.

Within f311, the code in :meth:`f311.convmol.conv_hitran.hitran_to_sols` contains a usage example of HITRAN data.

Conversion of molecular lines lists
===================================

Introduction
------------

Conversion between different formats of files containing molecular spectral lines data.

Conversion inputs:

- Robert Kurucz molecular line lists [Kurucz]_
- HITRAN Online database (partially implemented) [Gordon2016]_
- VALD3 [VALD3]_ (to do)
- TurboSpectrum [Plez]_ (to do)

Conversion output:

- PFANT molecular lines file (such as "molecules.dat")

Most relevant applications in F311 package
------------------------------------------

Graphical applications
^^^^^^^^^^^^^^^^^^^^^^

* :doc:`convmol.py <autoscripts/script-convmol>`: Conversion of molecular lines data to PFANT format
* :doc:`mced.py <autoscripts/script-mced>`: Editor for molecular constants file
* :doc:`moldbed.py <autoscripts/script-moldbed>`: Editor for molecules SQLite database

Command-line tools
^^^^^^^^^^^^^^^^^^

* :doc:`hitran-scraper.py <autoscripts/script-hitran-scraper>`: Retrieves molecular lines from the HITRAN database
* :doc:`nist-scraper.py <autoscripts/script-nist-scraper>`: Retrieves and prints a table of molecular constants from the NIST Chemistry Web Book [NIST]_.


How the conversion is made
--------------------------

List of symbols
~~~~~~~~~~~~~~~

Input molecular constants obtained from NIST database (all given in unit: cm**-1)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* *omega_e*: vibrational constant – first term
* *omega_ex_e*: vibrational constant – second term
* *omega_ey_e*: vibrational constant – third term
* *B_e*: rotational constant in equilibrium position
* *alpha_e*: rotational constant – first term
* *D_e*: centrifugal distortion constant
* *beta_e*: rotational constant – first term, centrifugal force
* *A*: Coupling counstant
* *M2l*: multiplicity of the initial state (1 for singlet, 2 for doublet, 3 for triplet and so on)
* *M2l*: multiplicity of the final state
* *LambdaL*: ?SPDF? of the initial state (0 for Sigma, 1 for Pi, 2 for Delta, 3 for Phi)
* *Lambda2L*: ?SPDF? of the initial state

.. hint::

    These values were downloaded from NIST for several molecules and can be navigated through in the applications ``convmol.py`` or ``mced.py``.

    Molecular constants can be downloaded from NIST using script ``nist-scraper.py``


Input data from line list files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* *lambda*: wavelength (angstrom)
* *vl*: vibrational quantum number of the initial state
* *v2l*: vibrational quantum number of the final state
* *spinl*
* *spin2l*
* *JL*: rotational quantum number of the initial state
* *J2l*: rotational quantum number of the final state

Calculated outputs
^^^^^^^^^^^^^^^^^^

The following values are calculated using application ``convmol.py`` and stored as a PFANT molecular lines file (such as "molecules.dat").

*Jl*/*J2l*-independent
++++++++++++++++++++++

* *qv*: Franck-Condon factor
* *Bv*: rotational constant
* *Dv*: rotational constant
* *Gv*: rotational constant

These terms are calculated as follows::

    qv = qv(molecule, system, vl, v2l) is calculated using the TRAPRB code [TRAPRB1970]
                                       The Franck-Condon factors were already calculate for several
                                       different molecules and are tabulated inside file "moldb.sqlite"

    Bv = B_e - alpha_e * (v2l + 0.5)

    Dv = (D_e + beta_e * (v2l + 0.5)) * 1.0e+06

    Gv = omega_e * (v2l + 0.5) - omega_ex_e * (v2l + 0.5) ** 2 + omega_ey_e * (v2l + 0.5) ** 3 -
         omega_e / 2.0 - omega_ex_e / 4.0 + omega_ey_e / 8.0


*Jl*/*J2l*-dependent (*i.e.*, for each spectral line)
+++++++++++++++++++++++++++++++++++++++++++++++++++++

* *LS*: line strength for given by formulas in [Kovacs1969]_, Chapter 3; Hönl-London factor
* *S*: normalized line strength

*LS* is calculated using a different formula depending on:

i. the multiplicities of the transition (currently implemented only cases where the initial and
   final state have same multiplicity)
ii. the value and/or sign of (*DeltaLambda* = *LambdaL* - *Lambda2l*);
iii. whether *A* is a positive or negative number;
iv. the branch of the spectral line (see below how to determine the branch)

So::

    formula = KovacsFormula(i, ii, iii, iv)

    LS = formula(almost every input variable)


.. hint::

    All the line strength formulas and logic to determine which formula to use are
    in module ``f311.physics.multiplicity``. The latter contains references to the formulas and
    tables from [Kovacs1969]_ that were used for each specific (i, ii, iii, iv) case.

.. todo::

    Explain term formulas "u+/-", "c+/-"

Normalization of the line strength
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Normalization is applied so that, for a given *J2l*,::

    sum([S[branch] for branch in all_branches]) == 1

To achieve this::

    S = LS * 2. / ((2 * spin2l + 1) * (2 * J2l + 1) * (2 - delta_k))

Where::

    spin2l = (M2l-1)/2

How to determine the branch
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The branch "label" follows one of the following conventions::

    singlets: branch consists of a "<letter>", where letter may be either "P", "Q", or "R"

    doublets, triplets etc:

        if spin == spinl == spin2l: branch consists of "<letter><spin>"

        if spinl <> spin2l: branch consists of "<letter><spinl><spin2l>"


The branch letter is determined as follows::

    if Jl < J2l:  "P"
    if Jl == J2l: "Q"
    if Jl > J2l:  "R"

API documentation
-----------------

:doc:`autodoc/f311.convmol`

Bibliography
------------
.. [Kovacs1969] Istvan Kovacs, Rotational Structure in the spectra of diatomic molecules. American Elsevier, 1969

.. [TRAPRB1970] Jarmain, W. R., and J. C. McCallum. "TRAPRB: a computer program for molecular
   transitions." University of Western Ontario (1970)

.. [NIST] http://webbook.nist.gov/chemistry/

.. [Kurucz] http://kurucz.harvard.edu/molecules.html

.. [VALD3] http://vald.astro.univie.ac.at/~vald3/php/vald.php

.. [Plez] http://www.pages-perso-bertrand-plez.univ-montp2.fr/

.. [Gordon2016] I.E. Gordon, L.S. Rothman, C. Hill, R.V. Kochanov, Y. Tan, P.F. Bernath, M. Birk,
   V. Boudon, A. Campargue, K.V. Chance, B.J. Drouin, J.-M. Flaud, R.R. Gamache, J.T. Hodges,
   D. Jacquemart, V.I. Perevalov, A. Perrin, K.P. Shine, M.-A.H. Smith, J. Tennyson, G.C. Toon,
   H. Tran, V.G. Tyuterev, A. Barbe, A.G. Császár, V.M. Devi, T. Furtenbacher, J.J. Harrison,
   J.-M. Hartmann, A. Jolly, T.J. Johnson, T. Karman, I. Kleiner, A.A. Kyuberis, J. Loos,
   O.M. Lyulin, S.T. Massie, S.N. Mikhailenko, N. Moazzen-Ahmadi, H.S.P. Müller, O.V. Naumenko,
   A.V. Nikitin, O.L. Polyansky, M. Rey, M. Rotger, S.W. Sharpe, K. Sung, E. Starikova,
   S.A. Tashkun, J. Vander Auwera, G. Wagner, J. Wilzewski, P. Wcisło, S. Yu, E.J. Zak,
   The HITRAN2016 Molecular Spectroscopic Database, J. Quant. Spectrosc. Radiat. Transf. (2017).
   doi:10.1016/j.jqsrt.2017.06.038.

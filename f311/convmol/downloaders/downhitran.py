"""
HITRAN Database [Gordon2016] downloader

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
"""

from robobrowser import RoboBrowser
import bs4
import re


__all__ = ["get_hitran_molecules", "get_hitran_isotopologues"]


def get_hitran_molecules():
    """
    Accesses http://hitran.org/lbl/# and reads its table
    Returns: tuple: table (list of lists), header (list of strings)
    """

    data, header = [], []


    browser = RoboBrowser(history=True, parser="lxml")
    browser.open("http://hitran.org/lbl/#")

    table = browser.find("table")

    hh = table.find_all("th")
    for h in hh:
        # Skips cells whose class starts with "meta" (they are not of interest)
        cls = h.get("class")
        if isinstance(cls, list) and cls[0].startswith("meta"):
            continue
        header.append(h.text)

    rr = table.find_all("tr")
    for r in rr:
        dd = r.find_all("td")
        if len(dd) == 0:
            continue
        row = []
        data.append(row)
        for d in dd:
            # Skips cells whose class starts with "meta" (they are not of interest)
            cls = d.get("class")
            if isinstance(cls, list) and cls[0].startswith("meta"):
                continue
            row.append(d.text)

    return data, header


def get_hitran_isotopologues(id_molecule):
    """
    Accesses http://hitran.org/lbl/2 and reads its table

    Args:
        id_molecule: molecule ID as in HITRAN database (use get_hitran_molecules() to get
                     this information)

    Returns: tuple: table (list of lists), header (list of strings)
    """

    data, header = [], []


    browser = RoboBrowser(history=True, parser="lxml")
    browser.open("http://hitran.org/lbl/2?{}=on".format(id_molecule))

    table = browser.find("table")

    hh = table.find_all("th")
    for h in hh:
        # Skips cells whose class starts with "meta" (they are not of interest)
        cls = h.get("class")
        if isinstance(cls, list) and cls[0].startswith("meta"):
            continue
        header.append(h.text)

    rr = table.find_all("tr")
    for r in rr:
        dd = r.find_all("td")
        if len(dd) == 0:
            continue
        row = []
        data.append(row)
        for i, d in enumerate(dd):
            # Skips cells whose class starts with "meta" (they are not of interest)
            cls = d.get("class")
            if isinstance(cls, list) and cls[0].startswith("meta"):
                continue

            if i == 1:
                # **Note** Assumes that "Formula" is the second field
                formula = re.match("<td>(.*)</td>", str(d)).group(1)
                text = _slugify_html_formula(formula)
            else:
                text = d.text
            row.append(text)

    return data, header
    # rows = table.find_all("tr")
    # n = 0
    # header = None
    # data = []  # list of lists
    # for row in rows:
    #     cols = row.find_all("td")
    #     flag_header = False
    #     if len(cols) == 0:
    #         if n > 0:
    #             continue
    #         # If no columns found, we assume it is the header row
    #         cols = row.find_all("th")
    #         header = [f_header(ele) for ele in cols]
    #     elif len(cols) == 13:
    #         row = [function(ele) for function, ele in zip(functions, cols)]
    #         data.append(row)
    #         n += 1
    #
    # # print(plain)
    # #
    # # print(rows_table)

    # return data, header, title


def _slugify_html_formula(formula):
    """Converts HTML formula to plain text (deals with HTML superscript and subscript tags)

    This function transforms superscript text into text between parentheses:
        '<sup>x</sup>' becomes '(x)'

    Also transforms subscript text into plain text:
       '<sub>x</sub>' becomes 'x'
    """

    formula = re.sub("<sup>(.+?)</sup>", lambda g: "({})".format(g.group(1)), formula)
    formula = re.sub("<sub>(.+?)</sub>", lambda g: "{}".format(g.group(1)), formula)

    return formula

if __name__ == "__main__":
    import tabulate
    data, header = get_hitran_molecules()
    print(tabulate.tabulate(data, header))

    data, header = get_hitran_isotopologues(4)
    print(tabulate.tabulate(data, header))

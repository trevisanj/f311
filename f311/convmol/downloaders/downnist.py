"""
NIST Downloader
"""
from robobrowser import RoboBrowser
import bs4
import re


__all__ = ["get_nist_webbook_constants", "NIST_URL"]

NIST_URL = "http://webbook.nist.gov/chemistry/form-ser.html"

_conv_sup = {"1": "\u2071",
             "2": "\u00b2",
             "3": "\u00b3",
             "4": "\u2074",
             "+": "\u207a",
             "-": "\u207b"}


_conv_img = {"larrow": "←",
             "rarrow": "→",
             "lrarrow": "↔"}


def _html_formula_to_unicode(tag):
    """
    Returns a string from a bs4.element.Tag representing a formula in NIST web book pages.

    Some HTML elements are converted to unicode characters
    """
    parts = []
    for item in tag.children:
        if isinstance(item, bs4.element.NavigableString):
            parts.append(str(item))
        elif item.name == "sub":
            parts.append("_" + item.text)
        elif item.name == "sup":
            parts.append(_conv_sup.get(item.text, "^" + item.text))
        elif item.name == "img":
            # parts.append("\\"+item.attrs["alt"])
            alt = item.attrs["alt"]
            parts.append(_conv_img.get(alt, alt))
    return ("".join(parts)).strip().replace("  ", " ").replace("  ", " ")


def _floatify(str_):
    """Tries to convert to float, stripping brackets if it is the case"""
    try:
        ret = float(str_)
    except:
        # Note: It seems that NIST Chemistry WebBook has some OCR behind.
        #       I am making some effort to go around some cases I bumped into, for example, : "4.7E-_7"

        gg = re.match("[\[(]*([0-9\.\-E]+)", str_.replace("_", ""))
        if gg is None:
            ret = str_
        else:
            ret = float(gg.groups()[0])
    return ret

def _nonify(x):
    """Returns None if len(x) == 0, else x"""
    if isinstance(x, str) and len(x.strip()) == 0:
        return None
    return x


# Callables to be used in different conversion situations
f_header = _html_formula_to_unicode
f_state = _html_formula_to_unicode
f_float_or_none = lambda x: _nonify(_floatify(_html_formula_to_unicode(x)))
f_str_or_none = lambda x: _nonify(_html_formula_to_unicode(x))
functions = [f_state]+[f_float_or_none]*10+[f_str_or_none, f_float_or_none]


def get_nist_webbook_constants(formula):
    """
    Navigates through NIST webbook pages to retrieve a table of molecular constants

    Args:
        formula: example: "OH"

    Returns: tuple: table (list of lists), header (list of strings), name of molecule

    **Disclaimer** This scraper matches a specific version of the Chemistry Web Book. Therefore,
    it may stop working if the NIST web site is updated.
    """
    browser = RoboBrowser(history=True, parser="lxml")
    browser.open("http://webbook.nist.gov/chemistry/form-ser.html")

    # # Page
    form = browser.get_form()
    form["Formula"].value = formula
    browser.submit_form(form)

    # # Molecule park page
    text = browser.find(text="Constants of diatomic molecules")

    if text is None:
        # # Probably fell in this page showing possible choices
        # In this case, clicks on the first choice

        ol = browser.find("ol")

        if not ol:
            raise RuntimeError("Constants of diatomic molecules not found for '{}'".format(formula))

        link0 = ol.find("a")

        if not link0:
            raise RuntimeError("Constants of diatomic molecules not found for '{}'".format(formula))
        browser.follow_link(link0)

        # # Molecule park page
        text = browser.find(text="Constants of diatomic molecules")
        link_ctes = text.parent
        browser.follow_link(link_ctes)
    else:
        link_ctes = text.parent
        browser.follow_link(link_ctes)

    # # Page

    title = browser.find("title").text

    table = browser.find("table", class_="small data")

    rows = table.find_all("tr")
    n = 0
    header = None
    data = []  # list of lists
    for row in rows:
        cols = row.find_all("td")
        flag_header = False
        if len(cols) == 0:
            if n > 0:
                continue
            # If no columns found, we assume it is the header row
            cols = row.find_all("th")
            header = [f_header(ele) for ele in cols]
            header.append("A")

        elif len(cols) == 13:

            row = [function(ele) for function, ele in zip(functions, cols)]
            row.append( parse_A(browser, cols[1]))
            data.append(row)
            n += 1

    # print(plain)
    #
    # print(rows_table)

    return data, header, title


def parse_A(browser, tag):
    """
    Parses the "A" information (A is the "coupling constant")

    The cell in column "Te" sometimes cites a reference; the anchor tag has an Id like "Dia19";
    the value we are looking for is in (roughly in the form "A = some_number"

    """
    for item in tag.children:
        if item.name == "a":
            try:
                id_ = re.match("#(Dia\d+)", item.get("href")).groups()[0]
                a = browser.find("a", id=id_)
                if a is not None:
                    td = a.next_element.next_element
                    stemp = re.match("<td>\s*A.*?=\s*([\(\)\+\-]*[0-9]+\.[0-9]+)", str(td)).groups()[0]
                    if stemp is None:
                        return None
                    try:
                        return float(stemp.replace("(", "").replace(")", ""))
                    except AttributeError:
                        # no match
                        return None
                    except ValueError:
                        # match, but no valid float
                        return None

            except AttributeError:
                pass


    return None
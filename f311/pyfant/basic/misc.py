# # Maybe I can use this one day. But the purpose was to validate elements, but confusing CO with Co is not nice

# import f311.ftpyfant as pf
# import a99
#
#
# __all__ = ["is_element"]
#
#
# __SYMBOLS_ADJUSTED = None
#
#
# def SYMBOLS_ADJUSTED():
#     global __SYMBOLS_ADJUSTED
#     if __SYMBOLS_ADJUSTED is None:
#         __SYMBOLS_ADJUSTED = [pf.adjust_atomic_symbol(x) for x in a99.symbols]
#     return __SYMBOLS_ADJUSTED
#
# def is_element(symbol):
#     """Returns True if symbol is an atomic element according to convention in adjust_atomic_symbol()
#
#     >>> is_element("CO")
#     False
#     >>> is_element("       fe   ")
#     True
#     """
#     return pf.adjust_atomic_symbol(symbol) in SYMBOLS_ADJUSTED()
#

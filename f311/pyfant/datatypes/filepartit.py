__all__ = ["FilePartit"]


import a99


class FilePartit(ex.DataFile):
    """
    PFANT Partition Function

    Reader/writer not implemented (will be implemented  when there is the need for so)
    """

    default_filename = "partit.dat"

    def __init__(self):
        ex.DataFile.__init__(self)

    def _do_load(self, filename):
        raise NotImplementedError("This class is a stub ATM")

    def _do_save_as(self, filename):
        raise NotImplementedError("This class is a stub ATM")

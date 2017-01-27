import a99
from .basic import Vis


__all__ = ["VisPrint"]


class VisPrint(Vis):
    """Prints object to screen."""

    input_classes = (object,)
    action = "Print to console"

    def _do_use(self, obj):
        print(obj)

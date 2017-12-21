import a99


__all__ = ["Vis", "VisList"]


class Vis(object):
    """
    Base class for visualizations.

    Those who open multiple figures must call plt.show(), otherwise not.
    """

    # Set the classes accepted by the use() method
    input_classes = ()
    # Fill string with a verb and object, e.g. "plot first record"
    action = ""

    def __init__(self):
        self.title = None
        self.parent_form = None

    def use(self, obj, parent_form=None):
        """Note: if title is None, will be replaced with obj.filename
        """

        if not isinstance(obj, self.input_classes):
            raise RuntimeError('{0!s} cannot handle a {1!s}'.format(self.__class__.__name__, obj.__class__.__name__))

        self.parent_form = parent_form

        if self.title is None:
            self.title = 'file: '+obj.filename
        self._do_use(obj)

    def _do_use(self, obj):
        raise NotImplementedError()


class VisList(Vis):
    """Vis subclass that can handle a list of objects to visualize simultaneously"""

    input_classes = (list)
    # Inform the element classes accepted
    item_input_classes = ()

    def use(self, objs, parent_form=None):
        for obj in objs:
            if not isinstance(obj, self.item_input_classes):
                raise RuntimeError('{0!s} cannot handle a {1!s}'.format(self.__class__.__name__, obj.__class__.__name__))

        self.parent_form = parent_form
        self._do_use(objs)

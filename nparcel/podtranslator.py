__all__ = [
    "PodTranslator",
]
import nparcel


class PodTranslator(nparcel.Service):
    """:class:`nparcelPodTranslator` object structure.
    """ 

    def __init__(self):
        nparcel.Service.__init__(self)

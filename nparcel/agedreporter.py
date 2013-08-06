__all__ = [
    "AgedParcelReporter",
]
import nparcel


class AgedParcelReporter(nparcel.Reporter):
    """Nparcel aged parcel reporter.
    """

    def __init__(self):
        """Nparcel AgedParcelReporter initialisation.
        """
        super(AgedParcelReporter, self).__init__()

__all__ = [
    "DeliveryPartner",
]
import nparcel


class DeliveryPartner(nparcel.Table):
    """DeliveryPartner table ORM.
    """

    def __init__(self):
        """DeliveryPartner initialiser.
        """
        super(DeliveryPartner, self).__init__(name='delivery_partner')

    @property
    def schema(self):
        return ['id INTEGER PRIMARY KEY',
                'name TEXT(25)']

__all__ = [
    "PrimaryElect",
]
import nparcel


class PrimaryElect(nparcel.Reminder):
    """Nparcel PrimaryElect class.

    .. attribute:: template_base

        override the standard location to search for the
        SMS XML template (default is ``~user_home/.nparceld/templates``)

    """
    def __init__(self,
                 db=None,
                 proxy=None,
                 scheme='http',
                 sms_api=None,
                 email_api=None):
        """Nparcel PrimaryElect initialisation.
        """
        super(nparcel.PrimaryElect, self).__init__(db=db,
                                                   proxy=proxy,
                                                   scheme=scheme,
                                                   sms_api=sms_api,
                                                   email_api=email_api)

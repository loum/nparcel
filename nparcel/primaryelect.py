__all__ = [
    "PrimaryElect",
]
import nparcel


class PrimaryElect(object):
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
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        if sms_api is None:
            sms_api = {}
        self.smser = nparcel.RestSmser(proxy=proxy,
                                       proxy_scheme=scheme,
                                       **sms_api)

        if email_api is None:
            email_api = {}
        self.emailer = nparcel.RestEmailer(proxy=proxy,
                                           proxy_scheme=scheme,
                                           **email_api)

        self._template_base = None

    @property
    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value

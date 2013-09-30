__all__ = [
    "Comms",
]
import os

import nparcel
from nparcel.utils.log import log


class Comms(object):
    """Nparcel Comms class.

    """
    _template_base = None

    def __init__(self,
                 db=None,
                 proxy=None,
                 scheme='http',
                 sms_api=None,
                 email_api=None,
                 comms_dir=None):
        """Nparcel Comms initialisation.
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

        self.set_comms_dir(comms_dir)

    @property
    def comms_dir(self):
        return self._comms_dir

    def set_comms_dir(self, value):
        if self._create_dir(value):
            self._comms_dir = value

    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value

    def _create_dir(self, dir):
        """Helper method to manage the creation of a directory.

        **Args:**
            dir: the name of the directory structure to create.

        **Returns:**
            boolean ``True`` if directory exists.

            boolean ``False`` if the directory does not exist and the
            attempt to create it fails.

        """
        status = True

        # Attempt to create the directory if it does not exist.
        if dir is not None and not os.path.exists(dir):
            try:
                log.info('Creating directory "%s"' % dir)
                os.makedirs(dir)
            except OSError, err:
                status = False
                log.error('Unable to create directory "%s": %s"' %
                          (dir, err))

        return status

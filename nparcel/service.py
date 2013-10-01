__all__ = [
    "Service",
]
import os

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import create_dir


class Service(object):
    """Nparcel base-Service class.

    .. attribute:: db

        :class:`nparcel.DbSession` object

    .. attribute:: comms_dir

        directory where comms files are sent for further processing

    """
    _comms_dir = None

    def __init__(self, db=None, comms_dir=None):
        """Nparcel Service initialisation.

        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        if comms_dir is not None:
            self.set_comms_dir(comms_dir)

    @property
    def comms_dir(self):
        return self._comms_dir

    def set_comms_dir(self, value):
        if create_dir(value):
            self._comms_dir = value

    def flag_comms(self, action, id, service, dry=False):
        """Prepare the comms file for further processsing.

        **Args:**
            *action*: type of communication (either ``sms`` or ``email``)

            *id*: the ``job_item.id`` for comms

            *service*: the comms service template

        **Kwargs:**
            *dry*: only report, do not actually execute

        **Returns:**
            ``True`` for processing success

            ``False`` for processing failure

        """
        status = True

        comms_file = "%s.%d.%s" % (action, id, service)
        abs_comms_file = os.path.join(self.comms_dir, comms_file)
        log.info('Writing comms file to "%s"' % abs_comms_file)
        try:
            if not dry:
                fh = open(abs_comms_file, 'w')
                fh.close()
        except IOError, err:
            log.error('Unable to open comms file %s: %s' %
                      (abs_comms_file, err))
            status = False

        return status

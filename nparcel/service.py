__all__ = [
    "Service",
]
import os

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import create_dir


class Service(object):
    """Service-base class.

    .. attribute:: db

        :class:`nparcel.DbSession` object

    .. attribute:: comms_dir

        directory where comms files are sent for further processing

    .. attribute:: alerts

        list if alerts that can be captured during the processing workflow

    .. attribute:: prod

        hostname of the production instance

    """
    _prod = None
    _facility = None
    _db = None
    _comms_dir = None
    _alerts = []

    def __init__(self, db=None, comms_dir=None):
        """Service initialisation.

        """
        self._facility = self.__class__.__name__

        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        if comms_dir is not None:
            self.set_comms_dir(comms_dir)

    def __del__(self):
        if self.db is not None:
            self.db.disconnect()

    @property
    def facility(self):
        return self._facility

    @property
    def prod(self):
        return self._prod

    def set_prod(self, value=None):
        self._prod = value.lower()
        log.debug('%s prod instance name set to "%s"' %
                  (self.facility, self.prod))

    @property
    def comms_dir(self):
        return self._comms_dir

    def set_comms_dir(self, value):
        if create_dir(value):
            self._comms_dir = value

    @property
    def alerts(self):
        return self._alerts

    def set_alerts(self, value=None):
        if value is not None:
            log.error(value)
            self.alerts.append(value)
        else:
            log.info('Resetting %s alerts' % self.__class__.__name__)
            del self._alerts[:]
            self._alerts = []

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

    def flag_comms_previous(self, action, id, service, dry=False):
        """Check if the comms file flag has already been set.

        Additionally, if the comms has errored (``*.err`` file exists)
        then comms event file should not be created.

        **Args:**
            *action*: type of communication (either ``sms`` or ``email``)

            *id*: the ``job_item.id`` for comms

            *service*: the comms service template

        **Returns:**
            ``True`` comms flag file has previously been set

            ``False`` comms flag has not been previously set

        """
        status = False

        comms_file = "%s.%d.%s" % (action, id, service)
        abs_comms_file = os.path.join(self.comms_dir, comms_file)
        log.debug('Checking if comms file "%s" set previously' %
                  abs_comms_file)

        if (os.path.exists(abs_comms_file + '.err') or
            os.path.exists(abs_comms_file)):
            status = True
            log.debug('Comms file "%s" previously set' % abs_comms_file)

        return status

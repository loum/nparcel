__all__ = [
    "Comms",
]
import os
import re
import time
import datetime

import nparcel
from nparcel.utils.log import log


class Comms(object):
    """Nparcel Comms class.

    """
    _hold_period = 691200
    _template_base = None

    def __init__(self,
                 hold_period=None,
                 db=None,
                 proxy=None,
                 scheme='http',
                 sms_api=None,
                 email_api=None,
                 comms_dir=None):
        """Nparcel Comms initialisation.
        """
        if hold_period is not None:
            self._hold_period = hold_period

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
    def hold_period(self):
        return self._hold_period

    def set_hold_period(self, value):
        self._hold_period = value

    @property
    def comms_dir(self):
        return self._comms_dir

    def set_comms_dir(self, value):
        if self._create_dir(value):
            self._comms_dir = value

    @property
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

    def send_sms(self,
                 item_details,
                 template='sms_rem',
                 dry=False):
        """Send out reminder SMS comms.

        **Args:**
            *item_details*: dictionary of SMS details similar to::

                {'name': 'Vermont South Newsagency',
                 'address': 'Shop 13-14; 495 Burwood Highway',
                 'suburb': 'VERMONT',
                 'postcode': '3133',
                 'item_nbr': '12345678',
                 'phone_nbr': '0431602135',
                 'date': '2013 09 15'}

        **Kwargs:**
            *template*: the XML template used to generate the SMS content

            *dry*: only report, do not actual execute

        **Returns:**
            ``True`` for processing success

            ``False`` for processing failure

        """
        status = True

        mobile = item_details.get('phone_nbr')
        if mobile is None or not mobile:
            log.error('No SMS mobile contact provided')
            status = False

        if status and not self.smser.validate(mobile):
            status = False
            log.error('SMS mobile "%s" did not validate' % mobile)

        if status:
            log.info('Sending customer SMS to "%s"' % str(mobile))

            # OK, generate the SMS structure.
            base_dir = self.template_base
            sms_data = self.smser.create_comms(data=item_details,
                                               template=template,
                                               base_dir=base_dir)
            status = self.smser.send(data=sms_data, dry=dry)

        return status

    def get_return_date(self, created_ts):
        """Creates the return date in a nicely formatted output.

        Dates could be string based ("2013-09-19 08:52:13.308266") or
        a :class:`datetime.datetime` object.

        **Args:**
            *created_ts*: the date the parcel was created

        **Returns:**
            string representation of the "return to sender" date in the
            format "<Day full name> <day of month> <month> <year>".  For
            example::

                Sunday 15 September 2013

        """
        return_date = None

        log.debug('Preparing return date against "%s" ...' % created_ts)
        created_str = None
        if created_ts is not None:
            # Handle sqlite and MSSQL dates differently.
            if isinstance(created_ts, str):
                r = re.compile('(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.\d*')
                m = r.match(created_ts)
                try:
                    created_str = m.group(1)
                except AttributeError, err:
                    log.error('Date not found "%s": %s' % (created_ts, err))
            else:
                created_str = created_ts.strftime("%Y-%m-%d %H:%M:%S")
        if created_str is not None:
            ts = time.strptime(created_str, "%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.fromtimestamp(time.mktime(ts))
            returned_dt = dt + datetime.timedelta(seconds=self.hold_period)
            return_date = returned_dt.strftime('%A %d %B %Y')

        log.debug('Return date set as: "%s"' % return_date)

        return return_date

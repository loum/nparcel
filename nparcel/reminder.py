__all__ = [
    "Reminder",
]
import re
import time
import datetime

import nparcel
from nparcel.utils.log import log


class Reminder(object):
    """Nparcel Reminder class.

    .. attribute:: config

        path name to the configuration file

    .. attribute:: notification_delay

        period (in seconds) that triggers a delayed pickup (default is
        345600 seconds or 4 days)

    .. attribute:: start_date

        date when delayed notifications start

    .. attribute:: hold_period

        period (in seconds) that the uncollected parcel will be held for

    .. attribute:: template_base

        override the standard location to search for the
        SMS XML template (default is ``~user_home/.nparceld/templates``)

    """
    def __init__(self,
                 notification_delay=345600,
                 start_date=datetime.datetime(2013, 9, 10, 0, 0, 0),
                 hold_period=691200,
                 db=None,
                 proxy=None,
                 scheme='http',
                 sms_api=None,
                 email_api=None):
        """Nparcel Reminder initialisation.

        """
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        self._notification_delay = notification_delay
        self._start_date = datetime.datetime(2013, 9, 10, 0, 0, 0)
        self._hold_period = hold_period

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
    def notification_delay(self):
        return self._notification_delay

    def set_notification_delay(self, value):
        self._notification_delay = value

    @property
    def start_date(self):
        return self._start_date

    def set_start_date(self, value):
        self._start_date = value

    @property
    def hold_period(self):
        return self._hold_period

    def set_hold_period(self, value):
        self._hold_period = value

    @property
    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value

    def get_uncollected_items(self):
        """Generator which returns the uncollected job_item.id's.

        **Returns:**
            list of integer values that represent the job_item.id's of
            uncollected parcels.

        """
        job_items = []

        now = datetime.datetime.now()
        delayed_dt = datetime.timedelta(seconds=self.notification_delay)
        threshold_dt = now - delayed_dt
        sql = self.db.jobitem.uncollected_sql(self.start_date, threshold_dt)
        self.db(sql)

        for row in self.db.rows():
            yield row[0]

    def process(self, dry=False):
        """Identifies uncollected parcels and sends notifications.

        For each uncollected parcel (``job_item.id``), details such as
        Agent information, contact mobile and email and created timestamp
        are extracted from the database.

        A reminder message will be send to the customer if a valid mobile
        and/or email address is found.

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list of uncollected job_items that were successfully
            processed

        """
        processed_ids = []

        for id in self.get_uncollected_items():
            log.info('Preparing reminder notice for job_item.id: %d' % id)
            template_details = self.get_agent_details(id)

            returned_date = template_details.get('created_ts')
            template_details['date'] = self.get_return_date(returned_date)

            email_status = self.send_email(template_details,
                                           template='rem',
                                           err=False,
                                           dry=dry)
            sms_status = self.send_sms(template_details,
                                       template='sms_rem',
                                       dry=dry)

            if not sms_status or not email_status:
                log.info('Sending comms failure notification to "%s"' %
                          self.emailer.support)
                for addr in self.emailer.support:
                    template_details['email_addr'] = addr
                    email_status = self.send_email(template_details,
                                                   template='rem',
                                                   err=True,
                                                   dry=dry)
            else:
                log.info('Setting job_item %d reminder sent flag' % id)
                if not dry:
                    self.db(self.db.jobitem.update_reminder_ts_sql(id))
                processed_ids.append(id)

        return processed_ids

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

    def get_agent_details(self, agent_id):
        """Get agent details.

        **Args:**
            agent_id: as per the agent.id table column

        **Returns:**
            dictionary structure capturing the Agent's details similar to::

                {'name': 'Vermont South Newsagency',
                 'address': 'Shop 13-14; 495 Burwood Highway',
                 'suburb': 'VERMONT',
                 'postcode': '3133',
                 'connote': 'abcd',
                 'item_nbr': '12345678',
                 'created_ts': '2013-09-15 00:00:00'}

        """
        agent_details = {}

        sql = self.db.jobitem.job_item_agent_details_sql(agent_id)
        self.db(sql)
        columns = self.db.columns()
        log.debug('columns: %s' % columns)
        agents = []
        for row in self.db.rows():
            agents.append(row)

        if len(agents) != 1:
            log.error('job_item.id %d agent list: "%s"' % (id, agents))
        else:
            agent_details = [None] * (len(columns) + len(agents[0]))
            agent_details[::2] = columns
            agent_details[1::2] = agents[0]
            log.debug('job_item.id %d detail: "%s"' % (agent_id, agents[0]))

        return dict(zip(agent_details[0::2], agent_details[1::2]))

    def send_email(self,
                   item_details,
                   template='body',
                   err=False,
                   dry=False):
        """Send out email comms to the list of *to_addresses*.

        **Args:**
            *item_details*: dictionary of details expected by the email
            template similar to::

                {'name': 'Vermont South Newsagency',
                 'address': 'Shop 13-14; 495 Burwood Highway',
                 'suburb': 'VERMONT',
                 'postcode': '3133'}

        **Kwargs:**
            *template*: the HTML body template to use

            *dry*: only report, do not actual execute

        **Returns:**
            ``True`` for processing success

            ``False`` for processing failure

        """
        status = True

        to_address = item_details.get('email_addr')
        if to_address is None:
            log.error('No email recipients provided')
            status = False

        item_nbr = item_details.get('item_nbr')
        if status and item_nbr is None:
            status = False
            err = 'Email reminder missing details: %s' % str(item_details)
            log.error(err)

        if status:
            self.emailer.set_recipients(to_address.split(','))
            subject = 'Toll Consumer Delivery parcel ref# %s' % item_nbr
            if err:
                subject = 'FAILED NOTIFICATION - ' + subject
            base_dir = self.template_base
            encoded_msg = self.emailer.create_comms(subject=subject,
                                                    data=item_details,
                                                    base_dir=base_dir,
                                                    template=template,
                                                    err=err)
            status = self.emailer.send(data=encoded_msg, dry=dry)

        return status

    def send_sms(self,
                 item_details,
                 template='sms_rem',
                 dry=False):
        """Send out reminder SMS comms to the list of *mobiles*.

        **Args:**
            item_details: dictionary of SMS details similar to::

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

        item_nbr = item_details.get('item_nbr')
        if status and item_nbr is None:
            status = False
            err = 'SMS reminder missing item_nbr: %s' % str(item_details)
            log.error(err)

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

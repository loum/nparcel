__all__ = [
    "Reminder",
]
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

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list of uncollected job_items that were successfully
            processed

        """
        processed_ids = []

        for id in self.get_uncollected_items():
            log.info('Identified uncollected job_item.id: %d' % id)
            template_details = self.get_agent_details(id)

            processed_ids.append(id)

        return processed_ids

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
        agents = []
        for row in self.db.rows():
            agents.append(row)

        if len(agents) == 1:
            log.debug('job_item.id %d detail: "%s"' % (agent_id, agents[0]))

            (name, addr, suburb, pc, connote, item_nbr, ts) = agents[0]
            agent_details = {'name': name,
                             'address': addr,
                             'suburb': suburb,
                             'postcode': pc,
                             'connote': connote,
                             'item_nbr': item_nbr,
                             'created_ts': ts}
        else:
            log.error('job_item.id %d agent list: "%s"' % (id, agents))

        return agent_details

    def send_email(self,
                   item_details,
                   base_dir=None,
                   template='body',
                   err=False,
                   dry=False):
        """Send out email comms to the list of *to_addresses*.

        **Args:**
            *agent*: dictionary of agent details similar to::

                {'name': 'Vermont South Newsagency',
                 'address': 'Shop 13-14; 495 Burwood Highway',
                 'suburb': 'VERMONT',
                 'postcode': '3133'}

            *to_addresses*: list of email recipients

        **Kwargs:**
            *template*: the HTML body template to use

            *dry*: only report, do not actual execute

        **Returns:**
            ``True`` for processing success

            ``False`` for processing failure

        """
        status = True

        to_address = item_details.get('email')
        if to_address is None:
            log.error('No email recipients provided')
            status = False

        item_nbr = item_details.get('item_nbr')
        if status and item_nbr is None:
            status = False
            err = 'Email reminder missing details: %s' % str(item_details)
            log.error(err)

        if status:
            d = {'name': item_details.get('name'),
                 'address': item_details.get('address'),
                 'suburb': item_details.get('suburb'),
                 'postcode': item_details.get('postcode'),
                 'connote': item_details.get('connote'),
                 'item_nbr': item_nbr,
                 'date': item_details.get('date')}
            log.debug('Sending customer email to "%s"' % to_address)

            self.emailer.set_recipients([to_address])
            subject = 'Toll Consumer Delivery parcel ref# %s' % item_nbr
            if err:
                subject = 'FAILED NOTIFICATION - ' + subject
            encoded_msg = self.emailer.create_comms(subject=subject,
                                                    data=d,
                                                    base_dir=base_dir,
                                                    template=template,
                                                    err=err)
            status = self.emailer.send(data=encoded_msg, dry=dry)

        return status

    def send_sms(self,
                 item_details,
                 base_dir=None,
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
                 'mobile': '0431602135',
                 'date': '2013 09 15'}

        **Kwargs:**
            *template*: the XML template used to generate the SMS content

            *base_dir*: override the standard location to search for the
            SMS XML template (default is ``~user_home/.nparceld/templates``)

            *dry*: only report, do not actual execute

        **Returns:**
            ``True`` for processing success

            ``False`` for processing failure

        """
        status = True

        mobile = item_details.get('mobile')
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
            d = {'name': item_details.get('name'),
                 'address': item_details.get('address'),
                 'suburb': item_details.get('suburb'),
                 'postcode': item_details.get('postcode'),
                 'item_nbr': item_nbr,
                 'date': item_details.get('date')}
            log.debug('Sending customer SMS to "%s"' % str(mobile))
            d['mobile'] = mobile

            # OK, generate the SMS structure.
            sms_data = self.smser.create_comms(data=d,
                                               template=template,
                                               base_dir=base_dir)
            status = self.smser.send(data=sms_data, dry=dry)

        return status

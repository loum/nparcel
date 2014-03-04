__all__ = [
    "Comms",
]
import os
import re
import time
import datetime

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import (remove_files,
                                 move_file)
from nparcel.timezone import convert_timezone


class Comms(nparcel.Service):
    """Nparcel Comms class.

    .. attribute:: hold_period

        period (in seconds) that the uncollected parcel will be held for

    .. attribute:: template_tokens

        list of template tokens that are currently supported.  Possible
        values include ``body``, ``rem``, ``delay``, ``pe`` and ``ret``.
        Default ``body``

    .. attribute:: returns_template_tokens

        list of template tokens that extracts template detail from the
        ``returns`` table (default ``[ret]``)

    """
    _facility = None
    _hold_period = 691200
    _template_tokens = ['body']
    _returns_template_tokens = ['ret']

    def __init__(self, **kwargs):
        """Nparcel Comms initialisation.
        """
        self._facility = self.__class__.__name__

        db_kwargs = kwargs.get('db')
        comms_dir = kwargs.get('comms_dir')
        nparcel.Service.__init__(self, db=db_kwargs, comms_dir=comms_dir)

        if kwargs.get('hold_period') is not None:
            self._hold_period = kwargs.get('hold_period')

        proxy = kwargs.get('proxy')
        proxy_scheme = kwargs.get('scheme')
        sms_api = kwargs.get('sms_api')
        if sms_api is None:
            sms_api = {}
        email_api = kwargs.get('email_api')
        if email_api is None:
            email_api = {}

        self._smser = nparcel.RestSmser(proxy=proxy,
                                        proxy_scheme=proxy_scheme,
                                        **sms_api)

        self._emailer = nparcel.RestEmailer(proxy=proxy,
                                            proxy_scheme=proxy_scheme,
                                            **email_api)

    @property
    def hold_period(self):
        return self._hold_period

    def set_hold_period(self, value):
        self._hold_period = value

    @property
    def template_tokens(self):
        return self._template_tokens

    def set_template_tokens(self, values=None):
        del self._template_tokens[:]
        self._template_tokens = []

        if values is not None:
            self._template_tokens.extend(values)
        log.debug('%s template_tokens set to: "%s"' %
                  (self._facility, self.template_tokens))

    @property
    def returns_template_tokens(self):
        return self._returns_template_tokens

    def set_returns_template_tokens(self, values=None):
        del self._returns_template_tokens[:]
        self._returns_template_tokens = []

        if values is not None:
            self._returns_template_tokens.extend(values)
        log.debug('%s returns_template_tokens set to: "%s"' %
                  (self._facility, self.returns_template_tokens))

    def process(self, comms_file, dry=False):
        """Attempts to send comms via appropratie medium based on
        *comms_file* comms event file.

        Successful notifications will set the ``job_item.notify`` column
        if the corresponding ``job_item.id``.

        **Args:**
            *comms_file*: the name of the comms file to process.

        **Kwargs:**
            *dry*: only report, do not execute (default ``False``)

        **Returns:**
            boolean ``True`` if *comms_file* is processed successfully

            boolean ``False`` otherwise

        """
        log.info('Processing comms file: "%s" ...' % comms_file)
        action = None
        id = None
        template = None
        comms_file_err = comms_file + '.err'
        comms_status = True
        filename = os.path.basename(comms_file)

        try:
            (action, id, template) = self.parse_comms_filename(filename)
        except ValueError, err:
            log.error('%s processing error: %s' % (comms_file, err))
            if not dry:
                move_file(comms_file, comms_file_err)
            comms_status = False

        if comms_status:
            template_items = self.get_agent_details(id, template)
            if not template_items.keys():
                log.error('%s processing error: %s' %
                          (comms_file, 'no agent details'))
                if not dry:
                    move_file(comms_file, comms_file_err)
                comms_status = False
            elif template_items.get('pickup_ts'):
                log.warn('%s pickup_ts has been set -- not sending comms' %
                         comms_file)
                if not dry:
                    remove_files(comms_file)
                comms_status = False

        if comms_status:
            recipient = None
            created_ts = template_items.get('created_ts')
            if template == 'rem':
                template_items['date'] = self.get_return_date(created_ts)
            elif template == 'ret':
                state = template_items.get('state')
                if state is not None:
                    state = state.rstrip()
                    local_time = convert_timezone(created_ts,
                                                  state,
                                                  '%d/%m/%Y %I:%M%p')
                    template_items['created_ts'] = local_time

            if action == 'email':
                recipient = template_items.get('email_addr')
                if recipient is not None:
                    recipient = recipient.strip()
                if recipient is not None and recipient:
                    comms_status = self.send_email(template_items,
                                                   template=template,
                                                   err=False,
                                                   dry=dry)
                else:
                    log.info('Email recipients list is empty')
            elif action == 'sms':
                recipient = template_items.get('phone_nbr')
                if recipient is not None:
                    recipient = recipient.strip()
                if recipient is not None and recipient:
                    comms_status = self.send_sms(template_items,
                                                 template=template,
                                                 dry=dry)
                else:
                    log.info('SMS is empty')
            else:
                log.error('Unknown action: "%s"' % action)
                comms_status = False

            if not comms_status:
                if not dry:
                    move_file(comms_file, comms_file_err)
                bad_email = template_items['email_addr']
                template_items['bad_email_addr'] = bad_email
                template_items['error_comms'] = action.upper()
                for addr in self._emailer.support:
                    template_items['email_addr'] = addr
                    email_status = self.send_email(template_items,
                                                   template=template,
                                                   err=True,
                                                   dry=dry)
            else:
                if recipient is not None and recipient:
                    if template == 'rem':
                        log.info('Setting job_item %d reminder flag' % id)
                        self.db(self.db.jobitem.update_reminder_ts_sql(id))
                    else:
                        log.info('Setting job_item %d notify flag' % id)
                        self.db(self.db.jobitem.update_notify_ts_sql(id))

                    if not dry:
                        self.db.commit()

                log.info('Removing comms file: "%s"' % comms_file)
                if not dry:
                    remove_files(comms_file)

        log.debug('Comms status: %s' % str(comms_status))

        return comms_status

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

        if status and not self._smser.validate(mobile):
            status = False
            log.error('SMS mobile "%s" did not validate' % mobile)

        if status:
            log.info('Sending customer SMS to "%s"' % str(mobile))

            # OK, generate the SMS structure.
            sms_data = self._smser.create_comms(data=item_details,
                                                template=template)
            status = self._smser.send(data=sms_data, dry=dry)

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
        subject = ''
        if status and item_details.keys() > 1:
            subject = self._emailer.get_subject_line(item_details,
                                                     template=template)
            subject = subject.rstrip('\n')

        if status:
            self._emailer.set_recipients(to_address.split(','))
            if err:
                log.info('Sending comms failure notification to "%s"' %
                          str(self._emailer.support))
                subject = 'FAILED NOTIFICATION - ' + subject
            else:
                log.info('Sending customer email to "%s"' %
                         str(self._emailer.recipients))
            encoded_msg = self._emailer.create_comms(subject=subject,
                                                     data=item_details,
                                                     template=template,
                                                     err=err)
            status = self._emailer.send(data=encoded_msg, dry=dry)

        return status

    def get_agent_details(self, table_id, template_token=None):
        """Get agent details.

        **Args:**
            *table_id*: as per the ``job_item.id`` table column for
            non-returns or ``returns.id`` otherwise

        **Kwargs:**
            *template_token*: template context.  Selection includes one of
            either ``body``, ``rem``, ``delay``, ``pe`` or ``ret``

        **Returns:**
            dictionary structure capturing the Agent's details similar to::

                {'name': 'Vermont South Newsagency',
                 'address': 'Shop 13-14; 495 Burwood Highway',
                 'suburb': 'VERMONT',
                 'postcode': '3133',
                 'connote': 'abcd',
                 'item_nbr': '12345678',
                 'pickup_ts': '',
                 'created_ts': '2013-09-15 00:00:00'}

        """
        agent_details = []

        agents = []
        tmp_agents = []
        if (template_token is None or
            template_token not in self.returns_template_tokens):
            sql = self.db.jobitem.job_item_agent_details_sql(table_id)
            self.db(sql)
            columns = self.db.columns()
            agents.extend(list(self.db.rows()))
        else:
            # Fugly hack because we can't get a group_concat in sqlite.
            sql = self.db.returns.extract_id_sql(table_id)
            self.db(sql)
            columns = self.db.columns()
            tmp_agents.extend(list(self.db.rows()))

            sql = self.db.returns_reference.reference_nbr_sql(table_id)
            self.db(sql)
            columns.extend(self.db.columns())
            refs = [x[0] for x in list(self.db.rows())]

            for agent in tmp_agents:
                with_refs = agent + (', '.join(refs), )
                agents.append(with_refs)

        if len(agents) != 1:
            log.error('"%s" table_id %d agent list: "%s"' %
                      (template_token, table_id, agents))
        else:
            agent_details = [None] * (len(columns) + len(agents[0]))
            agent_details[::2] = columns
            agent_details[1::2] = agents[0]
            log.debug('"%s" table_id %d detail: "%s"' %
                      (template_token, table_id, agents[0]))

        return dict(zip(agent_details[0::2], agent_details[1::2]))

    def parse_comms_filename(self, filename):
        """Parse the comm *filename* and extract the job_item.id
        and template.

        Tokens that are supported must be listed in
        :attr:`template_tokens`

        **Args:**
            *filename*: the filename to parse

        **Returns:**
            tuple representation of the *filename* in the form::

                (<action>, <id>, "<template>")

            For example::

                ("email", 1, "pe")

        """
        comm_parse = ()

        log.debug('Parsing comms filename: "%s"' % filename)
        r = re.compile('(email|sms)\.(\d+)\.(%s)' %
                       '|'.join(self.template_tokens))
        m = r.match(filename)
        if m:
            try:
                comm_parse = (m.group(1), int(m.group(2)), m.group(3))
            except IndexError, err:
                log.error('Unable to parse filename "%s": %s' %
                          (filename, err))

        log.debug('Comms filename produced: "%s"' % str(comm_parse))

        return comm_parse

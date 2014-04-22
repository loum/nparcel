__all__ = [
    "OnDelivery",
]
import nparcel
from nparcel.utils.log import log


class OnDelivery(nparcel.Service):
    """OnDelivery class.

    .. attribute:: parser

        :mod:`nparcel.StopParser` parser object

    .. attribute:: ts_db_kwargs

        dictionary structure of key/values representing the TransSend
        connection.  Typical format is::

            kwargs = {'host': 'host',
                      'user': 'user',
                      'password': 'password',
                      'port': 1521,
                      'sid': 'sid'}

    .. attribute:: delivered_header

        string that represents the TransSend column header name for
        a delivered item (default ``latest_scan_event_action``)

    .. attribute:: delivered_event_key

        string that represents a delivered event
        (default ``delivered``)

    .. attribute:: scan_desc_header

        string that represents the TransSend column name for the
        latest scanned description (default ``latest_scanner_description``)

    .. attribute:: scan_desc_keys

        list of strings that represents a scanned description
        that should be omitted from the search set

    .. attribute:: ts_db

        :mod:`cx_Oracle` object to manage the TransSend database
        connectivity

    """
    _parser = nparcel.StopParser()
    _ts_db_kwargs = None
    _delivered_header = 'latest_scan_event_action'
    _delivered_event_key = 'delivered'
    _scan_desc_header = 'latest_scanner_description'
    _scan_desc_keys = ['IDS - TOLL FAST GRAYS ONLINE']
    _ts_db = None

    def __init__(self, db_kwargs=None, ts_db_kwargs=None, comms_dir=None):
        """OnDelivery initialisation.

        """
        super(nparcel.OnDelivery, self).__init__(db=db_kwargs,
                                                 comms_dir=comms_dir)

        if ts_db_kwargs is not None:
            self._ts_db_kwargs = ts_db_kwargs
        self._ts_db = nparcel.OraDbSession(ts_db_kwargs)
        self._ts_db.connect()

    def __del__(self):
        if self.ts_db is not None:
            self.ts_db.disconnect()

    @property
    def parser(self):
        return self._parser

    @property
    def ts_db_kwargs(self):
        return self._ts_db_kwargs

    def set_ts_db_kwargs(self, value):
        self._ts_db_kwargs = value

    @property
    def delivered_header(self):
        return self._delivered_header

    @property
    def delivered_event_key(self):
        return self._delivered_event_key

    @property
    def scan_desc_header(self):
        return self._scan_desc_header

    def set_scan_desc_header(self, value):
        self._scan_desc_header = value
        log.debug('Set scan_desc_header to "%s"' % self._scan_desc_header)

    @property
    def scan_desc_keys(self):
        return self._scan_desc_keys

    def set_scan_desc_keys(self, values):
        del self._scan_desc_keys[:]
        self._scan_desc_keys = []

        if values is not None:
            log.debug('Set scan description keys "%s"' % str(values))
            self._scan_desc_keys.extend(values)

    @property
    def ts_db(self):
        return self._ts_db

    def get_primary_elect_job_item_id(self, connote):
        """Return ``jobitem.id`` whose connote is associated with a
        ``job`` that is defined *Primary Elect* (``job.service_code`` = 3).

        **Args:**
            *connote*: search key value relating to the ``job.card_ref_nbr``
            column.

        **Returns:**
            list of ids that match the search criteria

        """
        ids = []
        sql = self.db.jobitem.connote_base_primary_elect_job(connote)
        self.db(sql)
        for row in self.db.rows():
            ids.append(row[0])

        return ids

    def get_uncollected_job_items(self,
                                  service_code=3,
                                  bu_ids=None,
                                  delivery_partners=None,
                                  day_range=14):
        """Generator that returns the ``jobitem.id``,
        ``jobitem.connote_nbr`` and ``jobitem.item_nbr`` of uncollected
        *service_code* based job items.

        **Kwargs:**
            *service_code*: integer of ``job.service_code`` columns

            *bu_ids*: tuple of Business Unit ID integers to search against

            *delivery_partners*: tuple of strings relating to the Delivery
            Partner names to filter the uncollected ``job_items`` against.
            Delivery Partner relates to the ``delivery_partner.name``
            column values.  For example ``('Nparcel', 'ParcelPoint')``.

            *day_range*: number of days from current time to include
            in search (default 14.0 days)

        **Returns:**
            generator object which represents an uncollected job item
            in the form of a tuple data structure::

                (<jobitem.id>, <jobitem.connote_nbr>)

        """
        if bu_ids is None:
            bu_ids = (1, 2, 3)

        kwargs = {'service_code': service_code,
                  'bu_ids': bu_ids,
                  'delivery_partners': delivery_partners,
                  'day_range': day_range}
        sql = self.db.jobitem.uncollected_jobitems_sql(**kwargs)
        self.db(sql)
        for row in self.db.rows():
            yield row

    def process(self,
                template,
                service_code,
                bu_ids,
                job_items=None,
                in_files=None,
                day_range=14,
                delivery_partners=None,
                dry=False):
        """Checks whether an On Delivery parcel item has had comms sent.

        **Args:**
            *template*: the comms notification template to use.  For
            example, ``pe`` for the Primary Elect check

            *service_code*: ``job.service_code`` column value to use in the
            uncollected ``job_items`` table extraction

            *bu_ids*: the Business Unit IDs to use in the uncollected
            ``job_items`` table extraction

        **Kwargs:**
            *job_items*: list of ``(<id>, <connote>, <item_nbr>)``
            that can be fed into the process loop directly

            *in_files*: list of paths to the input file

            *day_range*: limit uncollected parcel search to within nominated
            value

            *delivery_partners*: tuple of strings relating to the Delivery
            Partner names to filter the uncollected ``job_items`` against.
            Delivery Partner relates to the ``delivery_partner.name``
            column values.  For example ``('Nparcel', 'ParcelPoint')``.

            *dry*: only report, do not execute

        **Returns:**
            list of primary elect job_items for whom notifications were
            successfully processed.  Successful represents whether a comms
            for email *and* SMS was produced.

        """
        processed_ids = []

        # Just in case, maintain backward compatibility with original
        # solution.
        if delivery_partners is None:
            delivery_partners = ('Nparcel', )

        if in_files is not None:
            self.parser.set_in_files(in_files)
            self.parser.read()

        if job_items is None:
            kwargs = {'service_code': service_code,
                      'bu_ids': bu_ids,
                      'day_range': day_range,
                      'delivery_partners': delivery_partners}
            job_items = self.get_uncollected_job_items(**kwargs)
        else:
            log.debug('Received job_items list inline')

        for (id, connote, item_nbr) in job_items:
            log.debug('Processing On Del id|connote|item: "%s|%s|%s ..."' %
                      (id, connote, item_nbr))

            delivered_status = False
            if (not self.flag_comms_previous('email', id, template) and
                not self.flag_comms_previous('sms', id, template)):
                if (self.parser.connote_delivered(connote, item_nbr) or
                    self.connote_delivered(connote, item_nbr)):
                    delivered_status = True

                if delivered_status:
                    log.debug('Preparing comms for job_item.id: %d' % id)
                    if not dry:
                        if (self.flag_comms('email', id, template) and
                            self.flag_comms('sms', id, template)):
                            processed_ids.append(id)

            log.debug('On Del id|connote|item: "%s|%s|%s" check complete' %
                      (id, connote, item_nbr))

        if in_files is not None:
            self.parser.purge()

        return processed_ids

    def connote_delivered(self, connote_nbr, item_nbr):
        """Check if *connote_nbr* and *item_nbr* has been delivered.

        Uses the TransSend database as source.

        **Args:**
            *connote_nbr*: Connote value relating to the
            ``transsend.connote_number`` column

            *item_nbr*: Item number value relating to the
            ``transsend.item_number`` column

        **Returns:**
            boolean ``True`` if the *connote*/*item_nbr* combination
            has been delivered

        """
        log.debug('TransSend check connote|item "%s|%s" delivery status' %
                  (connote_nbr, item_nbr))

        delivered = False
        if self.ts_db is not None:
            sql = self.ts_db.transsend.connote_sql(connote_nbr=connote_nbr,
                                                   item_nbr=item_nbr)
            self.ts_db(sql)

            headers = self.ts_db.columns()
            log.debug('Headers received: %s' % str(headers))
            index = headers.index(self.delivered_header)
            log.debug('Delivered header index: %d' % index)
            scan_index = headers.index(self.scan_desc_header)
            log.debug('Scanned desc header index: %d' % scan_index)

            for row in self.ts_db.rows():
                log.debug('TransSend "%s" value: "%s"' %
                          (self.delivered_header, row[index].lower()))

                # Check if the scanned description suggests that we need
                # to suppress the row.
                suppress = False
                for scanned_desc in self.scan_desc_keys:
                    log.debug('scanned desc|row value "%s|%s"' %
                              (scanned_desc, str(row[scan_index])))
                    if (row[scan_index] is not None and
                        row[scan_index].lower() == scanned_desc.lower()):
                        suppress = True
                        break

                log.debug('Suppress scanned desc row value "%s"?: %s' %
                          (row[scan_index], str(suppress)))
                if (not suppress and
                    row[index].lower() == self.delivered_event_key):
                    delivered = True
                    break

        if delivered:
            log.info('TransSend connote|item "%s|%s" delivery status: %s' %
                    (connote_nbr, item_nbr, delivered))

        return delivered

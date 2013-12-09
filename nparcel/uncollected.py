__all__ = [
    "Uncollected",
]
import nparcel
from nparcel.utils.log import log


class Uncollected(nparcel.Auditer):
    """Toll Parcel Portal base Uncollected class.

    .. attribute::
        *columns*: list of names of the query columns

    .. attribute::
        *delta_time_column*: raw column name to use for time delta
        (default ``JOB_TS`` which relates to the ``job.job_ts`` column)

    """
    _columns = []
    _delta_time_column = 'JOB_TS'

    def __init__(self, db_kwargs=None, bu_ids=None):
        """Uncollected initialiser.

        """
        super(nparcel.Uncollected, self).__init__(db_kwargs=db_kwargs,
                                                  bu_ids=bu_ids)

    @property
    def columns(self):
        return self._columns

    def set_columns(self, values=None):
        del self._columns[:]
        self._columns = []

        if values is not None:
            log.debug('Setting columns to "%s"' % values)
            self._columns.extend(values)
        else:
            log.debug('Cleared columns list')

    @property
    def delta_time_column(self):
        return self._delta_time_column

    def set_delta_time_column(self, value):
        self._delta_time_column = value
        log.debug('Set delta time column to "%s"' % self._delta_time_column)

    def process(self, id, dry=False):
        """Checks ``agent_stocktake`` table for items that exist
        in the Toll Parcel Portal and are uncollected and aged.

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``job_item`` IDs that have been reported uncollected
            by the Agent and qualify as being aged in the Toll Parcel
            Point database.

        """
        log.info('Uncollected (Aged) query for BU ID "%d" ...' % id)

        log.debug('Setting processed_ts column')
        ts_now = self.db.date_now()
        if not dry:
            sql = self.db.agent_stocktake.update_processed_ts_sql(ts_now)
            self.db(sql)
            self.db.commit()

        aged_jobitems = []

        sql = self.db.jobitem.reference_sql(bu_ids=(id,))
        self.db(sql)

        self.set_columns(self.db.columns())
        for i in self.db.rows():
            log.debug('Found job_item: %s' % str(i))
            aged_jobitems.append(i)

        translated_aged_jobitems = []
        for i in aged_jobitems:
            translated_aged_jobitems.append(self._translate_bu(self.columns,
                                                               i,
                                                               self.bu_ids))

        date_delta_jobitems = []
        for i in translated_aged_jobitems:
            delta_row = self.add_date_diff(self.columns,
                                           i,
                                           self.delta_time_column,
                                           ts_now)
            date_delta_jobitems.append(delta_row)
        tmp_hdrs_list = self.db.columns()
        tmp_hdrs_list.append('DELTA_TIME')
        self.set_columns(tmp_hdrs_list)

        return date_delta_jobitems

    def _cleanse(self, header, row):
        """Generic modififications to the raw query result.

        Mods include:
        * prepend ``=`` to the ``CONNOTE_NBR``, ``BARCODE`` and ``ITEM_NBR``
        columns

        **Args:**
            *header*: list of column headers

            *row*: tuple structure that represents the raw row result

        **Returns:**
            the altered *row* tuple structure

        """
        log.debug('Cleansing row "%s"' % str(row))

        tmp_row_list = list(row)

        for i in ['CONNOTE_NBR',
                  'BARCODE',
                  'ITEM_NBR',
                  'JOB_TS',
                  'CREATED_TS',
                  'NOTIFY_TS',
                  'PICKUP_TS']:
            index = header.index(i)
            log.debug('Prepending "=" to column|value "%s|%s"' %
                      (i, str(tmp_row_list[index])))
            if tmp_row_list[index] is None:
                tmp_row_list[index] = str()
            else:
                tmp_row_list[index] = '="%s"' % tmp_row_list[index]

        return tuple(tmp_row_list)

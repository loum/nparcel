__all__ = [
    "Uncollected",
]
import nparcel
from nparcel.utils.log import log


class Uncollected(nparcel.Auditer):
    """Toll Parcel Portal base Uncollected class.

    .. attribute::
        *columns*: list of names of the query columns

    """
    _columns = []

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

    def process(self):
        """Checks ``agent_stocktake`` table for items that exist
        in the Toll Parcel Portal and are uncollected and aged.

        **Returns:**
            list of ``job_item`` IDs that have been reported uncollected
            by the Agent and qualify as being aged in the Toll Parcel
            Point database.

        """
        log.info('Starting Uncollected (Aged) extraction ...')

        log.debug('Setting processed_ts column')
        ts_now = self.db.date_now()
        sql = self.db.agent_stocktake.update_processed_ts_sql(ts_now)
        self.db(sql)

        aged_jobitems = []

        sql = self.db.jobitem.reference_sql()
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

        return translated_aged_jobitems

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

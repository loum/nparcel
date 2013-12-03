__all__ = [
    "Uncollected",
]
import nparcel
from nparcel.utils.log import log


class Uncollected(nparcel.Auditer):
    """Toll Parcel Portal base Uncollected class.
    """

    def __init__(self, db_kwargs=None):
        """Uncollected initialiser.

        """
        super(nparcel.Uncollected, self).__init__(db_kwargs=db_kwargs)

    def process(self, dry=False):
        """Checks ``agent_stocktake`` table for items that exist
        in the Toll Parcel Portal and are uncollected and aged.

        **Kwargs:**
            *dry*: only report, do not execute

        **Returns:**
            list of ``job_item`` IDs that have been reported uncollected
            by the Agent and qualify as being aged in the Toll Parcel
            Point database.

        """
        log.info('Starting Uncollected (Aged) Report ...')

        aged_jobitem_ids = []

        sql = self.db.jobitem.reference_sql()
        self.db(sql)

        log.debug('Columns: %s' % self.db.columns())
        for i in self.db.rows():
            log.debug('Found job_item: %s' % str(i))
            aged_jobitem_ids.append(i)

        log.info('Uncollected (Aged) Report processing complete')

        return aged_jobitem_ids

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

        for i in ['CONNOTE_NBR', 'BARCODE', 'ITEM_NBR']:
            index = header.index(i)
            log.debug('Prepending "=" to column|value "%s|%s"' %
                      (i, str(tmp_row_list[index])))
            tmp_row_list[index] = '=%s' % tmp_row_list[index]

        return tuple(tmp_row_list)

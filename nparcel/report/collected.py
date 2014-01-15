__all__ = [
    "Collected",
]
import nparcel
from nparcel.utils.log import log


class Collected(nparcel.Auditer):
    """Toll Parcel Portal base Collected class.

    """
    def __init__(self, db_kwargs=None, bu_ids=None):
        """Collected initialiser.

        """
        super(nparcel.Collected, self).__init__(db_kwargs=db_kwargs,
                                                bu_ids=bu_ids)

    def process(self, id=None, dry=False):
        """Checks ``agent_stocktake`` table for items that have already
        have been flagged as collected in Toll Parcel Portal.

        **Args:**
            *id*: tuple of integer based values relating to the
            ``job.bu_id`` column

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``job_item`` IDs that have been reported uncollected
            by the Agent yet exist in Toll Parcel Point database as being
            collected.

        """
        log.info('Collected Agent Stocktake query ...')

        if id is None:
            id = tuple(self.bu_ids.keys())

        sql = self.db.jobitem.reference_sql(bu_ids=id, picked_up=True)
        self.db(sql)

        self.set_columns(self.db.columns())
        items = list(self.db.rows())

        tmp_hdrs_list = self.db.columns()
        tmp_hdrs_list.append('STOCKTAKE_CREATED_TS')
        self.set_columns(tmp_hdrs_list)

        collected_parcels = []
        for i in items:
            refs = []
            try:
                connote_index = self.columns.index('CONNOTE_NBR')
                if i[connote_index] is not None:
                    refs.append(i[connote_index])
                barcode_index = self.columns.index('BARCODE')
                if i[barcode_index] is not None:
                    refs.append(i[barcode_index])
                item_index = self.columns.index('ITEM_NBR')
                if i[item_index] is not None:
                    refs.append(i[item_index])
            except ValueError, err:
                    log.warn('Unmatched column in headers: %s' % err)

            sql = self.db.agent_stocktake.stocktake_created_date(*refs)
            self.db(sql)
            agent_stocktake_created_ts = self.db.row[0]
            tmp_row = list(i)
            tmp_row.append(str(agent_stocktake_created_ts))

            if self.filter_collected_parcels(self.columns, tmp_row):
                collected_parcels.append(tmp_row)

        cleansed_items = []
        for i in collected_parcels:
            cleansed_items.append(self._cleanse(self.columns, i))

        translated_bus = []
        for i in cleansed_items:
            translated_bus.append(self.translate_bu(self.columns,
                                                    i,
                                                    self.bu_ids))

        return translated_bus

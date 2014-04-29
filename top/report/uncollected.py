__all__ = [
    "Uncollected",
]
import nparcel
from nparcel.utils.log import log


class Uncollected(nparcel.Auditer):
    """Toll Parcel Portal Uncollected class.

    """
    def __init__(self,
                 db_kwargs=None,
                 bu_ids=None,
                 delivery_partners=None):
        """Uncollected initialiser.

        """
        nparcel.Auditer.__init__(self,
                                 db_kwargs=db_kwargs,
                                 bu_ids=bu_ids,
                                 delivery_partners=delivery_partners)

    def process(self, id, dry=False):
        """Checks ``agent_stocktake`` table for items that exist
        in the Toll Parcel Portal and are uncollected and aged.

        **Args:**
            *id*: tuple of integer based values relating to the
            ``job.bu_id`` column

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

        kwargs = {'bu_ids': (id,),
                  'delivery_partners': self.delivery_partners}
        sql = self.db.jobitem.reference_sql(**kwargs)
        self.db(sql)

        self.set_columns(self.db.columns())
        items = list(self.db.rows())

        cleansed_items = []
        for i in items:
            cleansed_items.append(self._cleanse(self.columns, i))

        # Filter out aged items.
        filtered_items = []
        for i in cleansed_items:
            if self.aged_item(self.columns, i):
                filtered_items.append(i)

        translated_aged_items = []
        for i in filtered_items:
            translated_aged_items.append(self.translate_bu(self.columns,
                                                           i,
                                                           self.bu_ids))

        date_delta_items = []
        for i in translated_aged_items:
            delta_row = self.add_date_diff(self.columns,
                                           i,
                                           self.delta_time_column,
                                           ts_now)
            date_delta_items.append(delta_row)

        tmp_hdrs_list = self.db.columns()
        tmp_hdrs_list.append('DELTA_TIME')
        self.set_columns(tmp_hdrs_list)

        return date_delta_items

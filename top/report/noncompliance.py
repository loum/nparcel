__all__ = [
    "NonCompliance",
]
import top
from top.utils.log import log


class NonCompliance(top.Auditer):
    """Toll Outlet Portal base NonCompliance class.

    """

    def __init__(self,
                 db_kwargs=None,
                 bu_ids=None,
                 delivery_partners=None):
        """NonCompliance initialiser.

        """
        top.Auditer.__init__(self,
                             db_kwargs=db_kwargs,
                             bu_ids=bu_ids,
                             delivery_partners=delivery_partners)

    def process(self, id=None, dry=False):
        """Identifies list of ``job_items`` found in Toll Outlet Portal
        but not scanned into ``agent_stocktake`` by the agent.

        **Kwargs:**
            *dry*: do not execute, only report

        **Returns:**
            list of ``job_items`` found in Toll Outlet Portal but not
            scanned into ``agent_stocktake``.

        """
        log.info('Stocktake non-compliance query ...')

        ts_now = self.db.date_now()

        jobitems = []
        cleansed_jobitems = []
        xlated_jobitems = []
        date_delta_jobitems = []

        bu_ids = tuple(self.bu_ids.keys())

        if len(bu_ids):
            kwargs = {'bu_ids': bu_ids,
                      'delivery_partners': self.delivery_partners}
            sql = self.db.jobitem.non_compliance_sql(**kwargs)
            self.db(sql)
            self.set_columns(self.db.columns())
            jobitems = list(self.db.rows())

            for i in jobitems:
                cleansed_jobitems.append(self._cleanse(self.columns, i))

            for i in cleansed_jobitems:
                kwargs = {'headers': self.columns,
                          'row': i,
                          'bu_ids': self.bu_ids}
                xlated_jobitems.append(self.translate_bu(**kwargs))
            for i in xlated_jobitems:
                delta_row = self.add_date_diff(self.columns,
                                               i,
                                               self.delta_time_column,
                                               ts_now)
                date_delta_jobitems.append(delta_row)

            tmp_hdrs_list = self.db.columns()
            tmp_hdrs_list.append('DELTA_TIME')
            self.set_columns(tmp_hdrs_list)
        else:
            log.warn('No BU IDs specified')

        log.info('Stocktake non-compliance query complete')

        return date_delta_jobitems

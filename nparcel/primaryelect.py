__all__ = [
    "PrimaryElect",
]
import nparcel
from nparcel.utils.log import log


class PrimaryElect(nparcel.Service):
    """Nparcel PrimaryElect class.

    .. attribute:: parser

        :mod:`nparcel.StopParser` parser object

    """
    _parser = nparcel.StopParser()

    @property
    def parser(self):
        return self._parser

    def __init__(self, db=None, comms_dir=None):
        """Nparcel PrimaryElect initialisation.

        """
        super(nparcel.PrimaryElect, self).__init__(db=db,
                                                   comms_dir=comms_dir)

    def get_primary_elect_job_item_id(self, connote):
        """Return ``jobitem.id`` whose connote is associated with a
        ``job`` that is defined *Primary Elect* (``job.service_code`` = 3).

        """
        ids = []
        sql = self.db.jobitem.connote_base_primary_elect_job(connote)
        self.db(sql)
        for row in self.db.rows():
            ids.append(row[0])

        return ids

    def get_uncollected_primary_elect_job_items(self):
        """Generator that returns the ``jobitem.id`` and
        ``jobitem.connote_nbr`` of uncollected Primary Elect job items.

        **Returns:**
            generator object which represents an uncollected job item
            in the form of a tuple data structure::

                (<jobitem.id>, <jobitem.connote_nbr>)

        """
        sql = self.db.jobitem.uncollected_primary_elect_jobitems_sql()
        self.db(sql)
        for row in self.db.rows():
            yield row

    def process(self, mts_file=None, dry=False):
        """Checks whether a Primary Elect job item has had comms sent.

        **Kwargs:**
            *mts_file*: path to the MTS delivery report file

            *dry*: only report, do not execute

        **Returns:**
            list of primary elect job_items for whom notifications were
            successfully processed.  Successful represents whether a comms
            for email *and* SMS was produced.

        """
        processed_ids = []

        if mts_file is not None:
            self.parser.set_in_file(mts_file)
            self.parser.read()

        for (id,
             connote,
             item_nbr) in self.get_uncollected_primary_elect_job_items():
            log.info('Checking MTS for PE id|connote|item: "%s|%s|%s"' %
                     (id, connote, item_nbr))
            if self.parser.connote_delivered(connote):
                log.info('Preparing comms flag for job_item.id: %d' % id)
                if (self.flag_comms('email', id, 'pe') and
                    self.flag_comms('sms', id, 'pe')):
                    processed_ids.append(id)
                else:
                    log.error('Comms flag error for job_item.id: %d' % id)

        if mts_file is not None:
            self.parser.purge()

        return processed_ids

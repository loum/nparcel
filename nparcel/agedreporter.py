__all__ = [
    "AgedParcelReporter",
]
import nparcel


class AgedParcelReporter(nparcel.Reporter):
    """Nparcel aged parcel reporter.
    """

    def __init__(self, age=604800, db=None):
        """Nparcel AgedParcelReporter initialisation.
        """
        self._age = age
        if db is None:
            db = {}
        self.db = nparcel.DbSession(**db)
        self.db.connect()

        super(AgedParcelReporter, self).__init__()

    @property
    def age(self):
        return self._age

    def set_age(self, value):
        self._age = value

    def get_aged_parcels(self):
        """Nparcel aged parcels generator.
        """
        sql = self.db.stocktake.aged_parcel_stocktake_sql(self._age)
        self.db(sql)
        for row in self.db.rows():
            yield row

    def get_aged_jobitems(self):
        """
        """
        sql = self.db.jobitem.aged_sql(self._age)
        self.db(sql)
        for row in self.db.rows():
            yield row

    def get_aged(self):
        """
        """
        sql = """SELECT *
FROM job_item
WHERE connote_nbr IN ('APPLES', 'SCANNED_01', 'DODGY_01')"""
        self.db(sql)
        for row in self.db.rows():
            yield row

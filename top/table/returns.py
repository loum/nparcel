__all__ = [
    "Returns",
]
import nparcel


class Returns(nparcel.Table):
    """Returns table ORM.
    """

    def __init__(self):
        """Returns initialiser.
        """
        super(Returns, self).__init__(name='returns', alias='r')

    @property
    def schema(self):
        return('id INTEGER PRIMARY KEY',
               'agent_id INTEGER',
               'created_ts TIMESTAMP',
               'processed_ts TIMESTAMP',
               'name TEXT(30)',
               'email_addr TEXT(60)',
               'phone_nbr TEXT(12)',
               'receipt_required TEXT(1)')

    def extract_id_sql(self, id, alias=None):
        """SQL wrapper to extract the returns against *id*.

        Detail extracted includes:

        * Agent detail

        * Return Reference information

        **Args:**
            *id*: the id relating to the job.bu_id value.

        **Kwargs:**
            *alias*: override the :attr:`alias` value

        **Returns:**
            the SQL string
        """
        old_alias = self.alias
        if alias is not None:
            self.set_alias(alias)

        sql = """SELECT %(alias)s.email_addr,
       %(alias)s.phone_nbr,
       %(alias)s.created_ts,
       ag.name,
       ag.address,
       ag.suburb,
       ag.postcode,
       ag.state
FROM %(name)s AS %(alias)s, agent AS ag
WHERE %(alias)s.id = %(id)d
AND ag.id = %(alias)s.agent_id""" % {'alias': self.alias,
                                     'name': self.name,
                                     'id': id}

        self.set_alias(old_alias)

        return sql

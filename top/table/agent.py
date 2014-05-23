__all__ = [
    "Agent",
]
import top


class Agent(top.Table):
    """Agent table ORM.
    """

    def __init__(self):
        """Agent initialisater.
        """
        super(Agent, self).__init__(name='agent')

    @property
    def schema(self):
        return ["id INTEGER PRIMARY KEY",
                "code TEXT(6)",
                "dp_id INTEGER",
                "dp_code TEXT(10)",
                "name TEXT(100)",
                "contact_name TEXT(30)",
                "phone_nbr TEXT(12)",
                "email TEXT(40)",
                "fax_nbr TEXT(12)",
                "address TEXT(80)",
                "suburb TEXT(30)",
                "postcode TEXT(4)",
                "state TEXT(3)",
                "opening_hours TEXT(180)",
                "notes TEXT(256)",
                "username TEXT(10)",
                "status INTEGER",
                "created_ts TIMESTAMP",
                "parcel_size_code INTEGER"]

    def check_agent_id(self, agent_code):
        """SQL wrapper to return return the "agent.id" value for a
        given *agent_code*.

        **Args:**
            agent_code: the Agent Code generally of the form "V001"

        **Returns:**
            the SQL command

        """
        sql = """SELECT id FROM agent WHERE code='%s'""" % agent_code

        return sql

    def agent_sql(self, id, alias='ag'):
        """SQL wrapper to return return Agent details of a given *id*.

        **Args:**
            *id*: the Agent's "agent.id" private key

        **Kwargs:**
            *alias*: override the table alias (default ``ag``)

        **Returns:**
            the SQL command

        """
        sql = """SELECT %(alias)s.name,
       %(alias)s.address,
       %(alias)s.suburb,
       %(alias)s.postcode,
       dp.name AS DP_NAME
FROM agent AS %(alias)s, delivery_partner AS dp
WHERE %(alias)s.id=%(id)d
AND ag.dp_id = dp.id""" % {'id': id,
                      'alias': alias}

        return sql

    def agent_code_sql(self, code, alias='ag'):
        """SQL wrapper to return the id associated with the ``agent.code``
        field.

        **Args:**
            *id*: the Agent's "agent.id" private key

        **Kwargs:**
            *alias*: override the table alias (default ``ag``)

        **Returns:**
            the SQL command

        """
        sql = """SELECT %(alias)s.id
FROM agent AS %(alias)s
WHERE %(alias)s.code='%(code)s'""" % {'code': code, 'alias': alias}

        return sql

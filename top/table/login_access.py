__all__ = [
    "LoginAccess",
]
import top


class LoginAccess(top.Table):
    """LoginAccess table ORM.
    """

    def __init__(self):
        """LoginAccess initialiser.
        """
        super(LoginAccess, self).__init__(name='login_access')

    @property
    def schema(self):
        return('username TEXT(10) PRIMARY KEY',
               'dp_id INTEGER',
               'sla_id INTEGER')

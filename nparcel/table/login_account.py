__all__ = [
    "LoginAccount",
]
import nparcel


class LoginAccount(nparcel.Table):
    """LoginAccount table ORM.
    """

    def __init__(self):
        """LoginAccount initialiser.
        """
        super(LoginAccount, self).__init__(name='login_account')

    @property
    def schema(self):
        return('username TEXT(10) PRIMARY KEY',
               'password TEXT(16)',
               'description TEXT(50)',
               'status INTEGER')

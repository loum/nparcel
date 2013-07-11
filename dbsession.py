__all__ = [
    "dbsession",
]
import sqlite
from nparcel.utils.log import log


class DbSession(object):
    """Nparcel DB session manager.
    """

    def __init__(self,
                 host='localhost'):
        self._localhost = host

    @property
    def localhost(self):
        return self._localhost

    def connect(self):
        """Create a database session based on class attributes.
        """
        db_session = None

        try:
            if self.localhost == 'localhost':
                db_session = sqlite.connect('test.db') 
                log.info('Database session creation OK')
        except:
            log.error('Database session creation failed')
            pass

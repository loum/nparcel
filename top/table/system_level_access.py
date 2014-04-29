__all__ = [
    "SystemLevelAccess",
]
import nparcel


class SystemLevelAccess(nparcel.Table):
    """SystemLevelAccess table ORM.
    """

    def __init__(self):
        """SystemLevelAccess initialiser.
        """
        super(SystemLevelAccess, self).__init__(name='system_level_access')

    @property
    def schema(self):
        return ['id INTEGER PRIMARY KEY',
                'description TEXT(50)']

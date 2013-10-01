__all__ = [
    "create_dir",
]
import os

from nparcel.utils.log import log


def create_dir(dir):
    """Helper method to manage the creation of a directory.

    **Args:**
        dir: the name of the directory structure to create.

    **Returns:**
        boolean ``True`` if directory exists.

        boolean ``False`` if the directory does not exist and the
        attempt to create it fails.

    """
    status = True

    # Attempt to create the directory if it does not exist.
    if dir is not None and not os.path.exists(dir):
        try:
            log.info('Creating directory "%s"' % dir)
            os.makedirs(dir)
        except OSError, err:
            status = False
            log.error('Unable to create directory "%s": %s"' % (dir, err))

    return status

__all__ = [
    "create_dir",
    "get_directory_files",
    "check_eof_flag",
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


def get_directory_files(path):
    """Generator that returns the files in the directory given by *path*.

    Does not include the special entries '.' and '..' even if they are
    present in the directory.

    **Args:**
        *path*: absolute path name to the directory

    **Returns:**
        each file in the directory as a generator

    """
    try:
        for file in os.listdir(path):
            file = os.path.join(path, file)
            if os.path.isfile(file):
                yield file
    except OSError, err:
        log.error(err)


def check_eof_flag(file):
    """Checks if *file* is a standard T1250 file by verifying if the last
    line contains the string ``%%EOF``

    **Args:**
        *file*: the absolute path to the T1250 file to verify.

    **Returns:**
        boolean ``True`` if *file* has an ``%%EOF`` delimiter

        boolean ``False`` otherwise

    """
    status = False

    log.debug('Checking file "%s" for T1250 EOF' % file)
    try:
        fh = open(file, 'r')
    except IOError, e:
        log.error('File open error "%s": %s' % (file, str(e)))
    else:
        try:
            fh.seek(-7, 2)
            eof_search = fh.readline()
        except IOError, e:
            log.info('File "%s" seek error: %s' % (file, str(e)))
            eof_search = str()

        fh.close()
        eof_search = eof_search.rstrip('\r\n')
        if eof_search == '%%EOF':
            log.debug('File "%s" EOF found' % file)
            status = True
        else:
            log.debug('File "%s" EOF NOT found' % file)

    return status

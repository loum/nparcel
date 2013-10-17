__all__ = [
    "create_dir",
    "get_directory_files",
    "check_eof_flag",
    "load_template",
]
import os
import string

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
        for line_length in [-7, -5]:
            try:
                fh.seek(line_length, 2)
                eof_search = fh.readline()
            except IOError, e:
                log.info('File "%s" seek error: %s' % (file, str(e)))
                eof_search = str()

            eof_search = eof_search.rstrip('\r\n')
            if eof_search == '%%EOF':
                log.debug('File "%s" last line length %d EOF found' %
                          (file, abs(line_length)))
                status = True
                break
            else:
                log.debug('File "%s" last line length %d EOF NOT found' %
                          (file, abs(line_length)))

        fh.close()

    return status


def move_file(source, target, err=False):
    """Attempts to move *source* to *target*.

    Checks if the *target* directory exists.  If not, will attempt to
    create before attempting the file move.

    **Args:**
        *source*: name of file to move

        *target*: filename of where to move *source* to

        *err*: boolean flag which will attempt to move *source* aside if
        the move fails.  Target fail name is *source*.err

    **Returns:**
        boolean ``True`` if move was successful

        boolean ``False`` if move failed

    """
    log.info('Moving "%s" to "%s"' % (source, target))
    status = False

    if create_dir(os.path.dirname(target)):
        try:
            os.rename(source, target)
            target_file = os.path.join(source, target)
        except OSError, err:
            status = False
            log.error('%s move to %s failed -- %s' % (source, target, err))

    if not status:
        try:
            target = '%s.err' % source
            os.rename(source, target)
        except OSError, err:
            log.error('%s move to %s failed -- %s' % (source, target, err))

    return status


def load_template(template, base_dir=None, **kwargs):
    """Load file *template* and substitute with *kwargs*.

    **Args:**
        *template*: file to load

    **Kwargs:**
        *base_dir*: directory where *template*

        *kwargs*: varargs expected by the template

    """
    dir = os.path.curdir
    if base_dir is not None:
        dir = base_dir

    query = None
    query_file = os.path.join(dir, template)
    log.debug('Extracting SQL from template: "%s"' % query_file)
    f = None
    try:
        f = open(query_file)
    except IOError, err:
        log.error('Unable to open SQL template "%s": %s' %
                    (query_file, err))

    if f is not None:
        query_t = f.read()
        f.close()
        query_s = string.Template(query_t)
        query = query_s.substitute(**kwargs)

        return query

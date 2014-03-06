__all__ = [
    "create_dir",
    "get_directory_files",
    "get_directory_files_list",
    "check_eof_flag",
    "load_template",
    "remove_files",
    "move_file",
    "copy_file",
    "check_filename",
    "gen_digest",
    "gen_digest_path",
    "xlsx_to_csv_converter",
]
import os
import re
import string
import shutil
import md5
import tempfile
import nparcel.openpyxl
import csv

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

    if dir is not None:
        if not os.path.exists(dir):
            log.info('Creating directory "%s"' % dir)
            try:
                os.makedirs(dir)
            except OSError, err:
                status = False
                log.error('Directory create error: %s' % err)
    else:
        log.error('Invalid directory name supplied "%s"' % dir)

    return status


def get_directory_files(path, filter=None):
    """Generator that returns the files in the directory given by *path*.

    Does not include the special entries '.' and '..' even if they are
    present in the directory.

    If *filter* is provided, will perform a regular expression match
    against the files within *path*.

    **Args:**
        *path*: absolute path name to the directory

    **Kwargs:**
        *filter*: :mod:`re` type pattern that can be input directly into
        the :func:`re.search` function

    **Returns:**
        each file in the directory as a generator

    """
    try:
        for file in os.listdir(path):
            file = os.path.join(path, file)
            if os.path.isfile(file):
                if filter is None:
                    yield file
                else:
                    r = re.compile(filter)
                    m = r.match(os.path.basename(file))
                    if m:
                        yield file
    except (TypeError, OSError), err:
        log.error('Directory listing error for %s: %s' % (path, err))


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
        for line_length in [-7, -6, -5]:
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


def move_file(source, target, err=False, dry=False):
    """Attempts to move *source* to *target*.

    Checks if the *target* directory exists.  If not, will attempt to
    create before attempting the file move.

    **Args:**
        *source*: name of file to move

        *target*: filename of where to move *source* to

    **Kwargs:**
        *err*: boolean flag which will attempt to move *source* aside if
        the move fails if set to ``True``.  Target fail name is *source*.err

        *dry*: only report, do not execute (but will create the target
        directory if it is missing)

    **Returns:**
        boolean ``True`` if move was successful

        boolean ``False`` if move failed

    """
    log.info('Moving "%s" to "%s"' % (source, target))
    status = False

    if os.path.exists(source):
        if not dry:
            if create_dir(os.path.dirname(target)):
                try:
                    os.rename(source, target)
                    status = True
                except OSError, error:
                    log.error('%s move to %s failed -- %s' % (source,
                                                              target,
                                                              error))
    else:
        log.warn('Source file "%s" does not exist' % str(source))

    if not status and err and not dry:
        try:
            if os.path.exists(source):
                target = '%s.err' % source
                os.rename(source, target)
        except OSError, error:
            log.error('%s move to %s failed -- %s' %
                      (source, target, error))

    return status


def copy_file(source, target):
    """Attempts to copy *source* to *target*.

    Guarantees an atomic copy.  In other word, *target* will not present
    on the filesystem until the copy is complete.

    Checks if the *target* directory exists.  If not, will attempt to
    create before attempting the file move.

    **Args:**
        *source*: name of file to move

        *target*: filename of where to copy *source* to

    **Returns:**
        boolean ``True`` if move was successful

        boolean ``False`` if move failed

    """
    log.info('Copying "%s" to "%s"' % (source, target))
    status = False

    if os.path.exists(source):
        if create_dir(os.path.dirname(target)):
            try:
                tmp_dir = os.path.dirname(target)
                tmp_target_fh = tempfile.NamedTemporaryFile(dir=tmp_dir)
                tmp_target = tmp_target_fh.name
                tmp_target_fh.close()
                shutil.copyfile(source, tmp_target)
                os.rename(tmp_target, target)
                status = True
            except (OSError, IOError), err:
                log.error('%s copy to %s failed -- %s' % (source,
                                                          target,
                                                          err))
    else:
        log.warn('Source file "%s" does not exist' % str(source))

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


def get_directory_files_list(path, filter=None):
    return list(get_directory_files(path, filter))


def remove_files(files):
    """Attempts to remove *files*

    **Args:**
        *files*: either a list of file to remove or a single filename
        string

    **Returns:**
        list of files successfully removed from filesystem

    """
    if not isinstance(files, list):
        files = [files]

    files_removed = []
    for file_to_remove in files:
        try:
            log.info('Removing file "%s"' % file_to_remove)
            os.remove(file_to_remove)
            files_removed.append(file_to_remove)
        except OSError, err:
            log.error('"%s" remove failed: %s' % (file_to_remove, err))

    return files_removed


def check_filename(file, format):
    """Parse filename string supplied by *file* and check that it
    conforms to *format*.

    **Args:**
        *file*: the filename string

        *format*: the :mod:`re` format string to match against

    **Returns:**
        boolean ``True`` if filename string conforms to *format*

        boolean ``False`` otherwise

    """
    status = False

    r = re.compile(format)
    m = r.match(os.path.basename(file))
    if m:
        status = True
        log.debug('File "%s" matches filter "%s"' % (file, format))
    else:
        log.debug('File "%s" did not match filter "%s"' % (file, format))

    return status


def gen_digest(value):
    """Generates a 64-bit checksum against *str*

    .. note::

        The digest is actually the first 8-bytes of the
        :func:`md5.hexdigest` function.

    **Args:**
        *value*: the string value to generate digest against

    **Returns:**
        8 byte digest containing only hexadecimal digits

    """
    digest = None

    if value is not None and isinstance(value, basestring):
        m = md5.new()
        m.update(value)
        digest = m.hexdigest()[0:8]
    else:
        log.error('Cannot generate digest against value: %s' % str(value))

    return digest


def gen_digest_path(value):
    """Helper funciton that handles the creation of digest-based directory
    path.  The digest is calculated from *value*.

    For example, the *value* ``193433`` will generate the directory path
    list::

        ['73', '73b0', '73b0b6', '73b0b66e']

    **Args:**
        *value*: the string value to generate digest against

    **Returns:**
        list of 8-byte segments that constitite the original 32-byte
        digest

    """
    digest = gen_digest(value)

    dirs = []
    if digest is not None:
        n = 2
        dirs = [digest[0:2 + (i * 2)] for i in range(0, len(digest) / n)]

    return dirs


def xlsx_to_csv_converter(xlsx_file):
    """Convert *xlsx_file* into a CSV file.

    Conversion will attempt to create the CSV file variant in the same
    directory as *xlsx_file*.

    **Args:**
        *xlsx_file*: name of the ``*.xlsx`` file to convert

    **Returns:**
        the name of the new, converted CSV file (or ``None`` otherwise)

    """
    log.debug('Attempting to convert xlsx file: "%s" to csv' % xlsx_file)

    file, extension = os.path.splitext(xlsx_file)
    target_file = None

    if (os.path.exists(xlsx_file) and extension == '.xlsx'):
        wb = nparcel.openpyxl.load_workbook(xlsx_file)
        sh = wb.get_active_sheet()

        target_file = os.path.join(os.path.dirname(xlsx_file),
                                   "%s.csv" % os.path.basename(file))

        fh = None
        try:
            fh = open(target_file, 'wb')
        except IOError, err:
            log.error('Unable to open file: "%s" - %s' % (target_file, err))

        if fh is not None:
            c = csv.writer(fh)
            for r in sh.rows:
                c.writerow([cell.value for cell in r])

            fh.close()
            log.info('Conversion produced file: "%s"' % target_file)
    elif extension == '.csv':
        target_file = xlsx_file
    else:
        log.info('"%s" is not an xlsx file' % xlsx_file)

    return target_file

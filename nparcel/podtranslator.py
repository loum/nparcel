__all__ = [
    "PodTranslator",
]
import tempfile
import time
import os

from nparcel.utils.log import log
from nparcel.utils.files import (copy_file,
                                 move_file,
                                 get_directory_files_list)


class PodTranslator(object):
    """:class:`nparcelPodTranslator` object structure.
    """

    def token_generator(self, dt=None):
        """Highly customised token generator that provides a unique,
        unambiguous numeric representation for a POD identifier.

        Seconds since epoch maintains a natural counter.  Token can be
        forced from a know :class:`datetime.datetime` object via the *dt*
        parameter.  Otherwise, if *dt* is ``None`` token generation is
        based on current time.

        **Kwargs:**
            *dt*: a :class:`datetime.datetime` object to override the token
            generator against.

        **Returns:**
            token representation of seconds since epoch that can be used
            in an unambiguous arrangement with ``job_item.id`` for POD
            naming

        """
        token = None

        epoch = 0
        if dt is not None:
            # Get the microsecond component.
            us = dt.microsecond / 1E6
            epoch = int((time.mktime(dt.timetuple()) + us) * 10)
        else:
            # Guarantee, sequential uniqueness.
            time.sleep(0.1)
            epoch = int(time.time() * 10)

        if epoch > 0:
            # Check that it's not above our threshold.
            if epoch < 20000000000:
                token = map(int, str(epoch))
                token[0] = 0
                token = ''.join(str(x) for x in token)
            else:
                log.error('Maximum seconds threshold breached: %d' % epoch)

        log.debug('Token value generated: "%s"' % token)
        return token

    def process(self, file, column='JOB_KEY', dry=False):
        """Will translated *column* values in *file* according to the
        :meth:`token_generator` method.  Upon success, will created a new
        file with the extension ``.xlated`` appended.

        **Args:**
            *file*: fully qualified name to the report file

            *column*: the column header name that typically relates to the
            signature file (default ``JOB_KEY``)

        **Returns:**
            list of new, translated tokens

        """
        log.info('Translating file "%s" ...' % file)

        # Create a temporary file that will hold our translated content.
        temp_fh = tempfile.NamedTemporaryFile()
        log.debug('Created temp file "%s"' % temp_fh.name)

        # Open the existing report file.
        fh = None
        try:
            fh = open(file)
        except IOError, err:
            log.error('Could not open file "%s"' % file)

        keys = []
        if fh is not None:
            # Consume the header and dump unconditionally.
            header = fh.readline().split('|')
            temp_fh.write('|'.join(header))

            job_key_index = None
            try:
                job_key_index = header.index(column)
            except ValueError, err:
                log.error('Unable to source "%s" from header: %s' %
                          (column, err))

            if job_key_index is not None:
                for line in fh:
                    token = self.token_generator()
                    fields = line.rsplit('|')
                    old_token = fields[job_key_index]
                    keys.append(token)
                    fields[job_key_index] = token
                    temp_fh.write('|'.join(fields))

                    # ... and rename the signature file.
                    self.rename_signature_files(os.path.dirname(file),
                                                old_token,
                                                token,
                                                dry=dry)

            fh.close()

        # Only copy the translated file if there is content (and not dry).
        if len(keys) and not dry:
            temp_fh.flush()
            copy_file(temp_fh.name, '%s.xlated' % file)
        temp_fh.close()

        return keys

    def rename_signature_files(self, dir, old_token, new_token, dry=False):
        """Search *dir* for files which match the filter *old_token*
        and rename with *new_token*.  The original file name extension
        will be retained.

        **Args:**
            *dir*: directory to search

            *old_token*: the token to use as a filter for file matches that
            will be renamed

            *new_token*: the new filename

        **Returns:**
            for the files that were renamed, a list of the new filenames

        """
        signature_files = []

        files = get_directory_files_list(dir, filter='%s\..*' % old_token)
        log.debug('Found old signature files: "%s"' % files)

        for f in files:
            (fn, ext) = os.path.splitext(f)
            target = os.path.join(os.path.dirname(f),
                                  '%s%s' % (new_token, ext))
            move_file(f, target, dry=dry)
            signature_files.append(target)

        return signature_files

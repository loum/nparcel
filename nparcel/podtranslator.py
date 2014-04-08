__all__ = [
    "PodTranslator",
]
import tempfile
import time

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import copy_file


class PodTranslator(nparcel.Service):
    """:class:`nparcelPodTranslator` object structure.
    """

    def __init__(self):
        nparcel.Service.__init__(self)

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
            time.sleep(0.5)
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

    def process(self, file, column='JOB_KEY'):
        """Will translated *column* values in *file* according to the
        :meth:`token_generator` method.  Upon success, will created a new
        file with the extension ``.xlated`` appended.

        **Args:**
            *file*: fully qualified name to the report file

            *column*: the column header name that typically relates to the
            signature file (default ``JOB_KEY``)

        **Returns:**

        """
        log.info('Translating file "%s" for JOB_KEYs' % file)

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

            try:
                job_key_index = header.index(column)
                for line in fh:
                    token = self.token_generator()
                    fields = line.rsplit('|')
                    keys.append(fields[job_key_index])
                    fields[job_key_index] = token
                    temp_fh.write('|'.join(fields))
            except ValueError, err:
                log.error('Unable to source "%s" from header: %s' %
                          (column, err))

            fh.close()

        # Only copy the translated file if there is content.
        if len(keys):
            temp_fh.flush()
            copy_file(temp_fh.name, '%s.xlated' % file)
        temp_fh.close()

        return keys

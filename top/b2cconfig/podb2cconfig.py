__all__ = [
    "PodB2CConfig",
]
import top
from top.utils.log import log
from top.utils.setter import (set_scalar,
                              set_list)


class PodB2CConfig(top.B2CConfig):
    """:class:`top.PodB2CConfig` captures the configuration items
    required for the ``tophealth`` facility.

    .. attribute:: pod_translator_loop

        time (seconds) between pod_translator_loop processing iterations

    .. attribute:: pod_dirs

        inbound directory location to look for exporter files to process

    .. attribute:: out_dir

        outbound directory to place transposed files

    .. attribute:: file_formats

        list of regular expressions that represent the type of files that
        can be parsed by the POD translator

    """
    _pod_translator_loop = 600
    _pod_dirs = []
    _out_dir = None
    _file_formats = []

    @property
    def pod_translator_loop(self):
        return self._pod_translator_loop

    @set_scalar
    def set_pod_translator_loop(self, value):
        pass

    @property
    def pod_dirs(self):
        return self._pod_dirs

    @set_list
    def set_pod_dirs(self, values=None):
        pass

    @property
    def out_dir(self):
        return self._out_dir

    def set_out_dir(self, value=None):
        self._out_dir = value
        log.debug('%s out_dir set to: "%s"' %
                  (self.facility, str(self.out_dir)))

    @property
    def file_formats(self):
        return self._file_formats

    def set_file_formats(self, values=None):
        del self._file_formats[:]
        self._file_formats = []

        if values is not None:
            self._file_formats.extend(values)
        log.debug('%s pod.file_formats set to "%s"' %
                  (self.facility, self.file_formats))

    def __init__(self, file=None):
        """:class:`top.PodB2CConfig` initialisation.
        """
        top.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        # These are the generic values that can be removed
        # after top.B2CConfig is refactored.
        kwargs = [{'section': 'dirs',
                   'option': 'archive',
                   'var': 'archive_dir',
                   'is_required': True},
                  {'section': 'timeout',
                   'option': 'pod_translator_loop',
                   'var': 'pod_translator_loop',
                   'cast_type': 'int'},
                  {'section': 'dirs',
                   'option': 'pod_in',
                   'var': 'pod_dirs',
                   'is_list': True},
                  {'section': 'pod',
                   'option': 'out_dir',
                   'is_required': True},
                  {'section': 'pod',
                   'option': 'file_formats',
                   'is_list': True}]

        for kw in kwargs:
            self.parse_scalar_config(**kw)

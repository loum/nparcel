__all__ = [
    "MapperB2CConfig",
]
import top
from top.utils.setter import (set_scalar,
                              set_list)


class MapperB2CConfig(top.B2CConfig):
    """:class:`top.MapperB2CConfig` captures the configuration items
    required for the ``topmapperd`` facility.

    .. attribute:: mapper_loop

        time (seconds) between mapper processing iterations.

    .. attribute:: pe_customer

        upstream provider of the T1250 files (default "gis")

    .. attribute:: mapper_in_dir

        inbound file directory.  This is where the mapper daemon checks
        for files to process

    .. attribute:: pe_in_file_format

        filename structure to parse for Primary Elect inbound
        (default 'T1250_TOL[PIF]_\d{14}\.dat')

    .. attribute:: pe_in_file_archive_string

        regular expression grouping structure for Primary Elect inbound
        filenames that represent the YYYYMMDD date sequence (default
        T1250_TOL[PIF]_(\d{8})\d{6}\.dat

    """
    _mapper_loop = 30
    _pe_customer = 'gis'
    _mapper_in_dirs = []
    _pe_in_file_format = 'T1250_TOL[PIF]_\d{14}\.dat'
    _pe_in_file_archive_string = 'T1250_TOL[PIF]_(\d{8})\d{6}\.dat'

    @property
    def mapper_loop(self):
        return self._mapper_loop

    @set_scalar
    def set_mapper_loop(self, value):
        pass

    @property
    def pe_customer(self):
        return self._pe_customer

    @set_scalar
    def set_pe_customer(self, value):
        pass

    @property
    def mapper_in_dirs(self):
        return self._mapper_in_dirs

    @set_list
    def set_mapper_in_dirs(self, values):
        pass

    @property
    def pe_in_file_format(self):
        return self._pe_in_file_format

    @set_scalar
    def set_pe_in_file_format(self, value):
        pass

    @property
    def pe_in_file_archive_string(self):
        return self._pe_in_file_archive_string

    @set_scalar
    def set_pe_in_file_archive_string(self, value):
        pass

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        kwargs = [{'section': 'dirs',
                   'option': 'archive',
                   'var': 'archive_dir',
                   'is_required': True},
                  {'section': 'timeout',
                   'option': 'mapper_loop',
                   'cast_type': 'int'},
                  {'section': 'dirs',
                   'option': 'mapper_in',
                   'var': 'mapper_in_dirs',
                   'is_list': True,
                   'is_required': True},
                  {'section': 'primary_elect',
                   'option': 'file_format',
                   'var': 'pe_in_file_format'},
                  {'section': 'primary_elect',
                   'option': 'file_archive_string',
                   'var': 'pe_in_file_archive_string'},
                  {'section': 'primary_elect',
                   'option': 'customer',
                   'var': 'pe_customer'}]
        for kw in kwargs:
            self.parse_scalar_config(**kw)

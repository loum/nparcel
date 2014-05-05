__all__ = [
    "AdpB2CConfig",
]
import top
from top.utils.setter import (set_scalar,
                              set_list,
                              set_dict)


class AdpB2CConfig(top.B2CConfig):
    """:class:`top.AdpB2CConfig` captures the configuration items
    required for the ``topadpd`` facility.

    .. attribute:: *adp_loop*

        time (seconds) between filter processing iterations.

    .. attribute:: *adp_dirs*

        directory list for ADP bulk load files (into ``agent`` table)

    .. attribute:: adp_file_formats

        list of regular expressions that represent the type of files that
        can be parsed by the ADP loader

    .. attribute:: code_header

        special ADP bulk insert header name that relates to the
        ``agent.code`` column.  This value is used as a unique
        identifier during the agent insert process

    .. attribute:: adp_headers

        dictionary of ``agent`` table columns to column headers in the
        ADP bulk insert file

    .. attribute:: delivery_partners

        list of "delivery_partner" table values

    .. attribute:: adp_default_passwords

        dictionary of delivery partner default passwords

    """
    _adp_loop = 30
    _adp_dirs = []
    _adp_file_formats = []
    _code_header = None
    _adp_headers = {}
    _delivery_partners = []
    _adp_default_passwords = {}

    @property
    def adp_loop(self):
        return self._adp_loop

    @set_scalar
    def set_adp_loop(self, value):
        pass

    @property
    def adp_dirs(self):
        return self._adp_dirs

    @set_list
    def set_adp_dirs(self, values=None):
        pass

    @property
    def adp_file_formats(self):
        return self._adp_file_formats

    @set_list
    def set_adp_file_formats(self, values=None):
        pass

    @property
    def code_header(self):
        return self._code_header

    @set_scalar
    def set_code_header(self, value):
        pass

    @property
    def adp_headers(self):
        return self._adp_headers

    @set_dict
    def set_adp_headers(self, values=None):
        pass

    @property
    def delivery_partners(self):
        return self._delivery_partners

    @set_list
    def set_delivery_partners(self, values=None):
        pass

    @property
    def adp_default_passwords(self):
        return self._adp_default_passwords

    @set_dict
    def set_adp_default_passwords(self, values=None):
        pass

    def __init__(self, file=None):
        """ExporterB2CConfig initialisation.
        """
        top.B2CConfig.__init__(self, file)

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        kwargs = [{'section': 'timeout',
                   'option': 'adp_loop',
                   'cast_type': 'int'},
                  {'section': 'dirs',
                   'option': 'adp_in',
                   'var': 'adp_dirs',
                   'is_list': True},
                  {'section': 'dirs',
                   'option': 'archive',
                   'var': 'archive_dir',
                   'is_required': True},
                  {'section': 'adp',
                   'option': 'file_formats',
                   'var': 'adp_file_formats',
                   'is_list': True},
                  {'section': 'adp',
                   'option': 'code_header'},
                  {'section': 'adp',
                   'option': 'delivery_partners',
                   'is_list': True}]
        for kw in kwargs:
            self.parse_scalar_config(**kw)

        del kwargs[:]
        kwargs = [{'section': 'adp_headers'},
                  {'section': 'adp_default_passwords'}]
        for kw in kwargs:
            self.parse_dict_config(**kw)

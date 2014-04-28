__all__ = [
    "FilterB2CConfig",
]
import nparcel
from nparcel.utils.setter import (set_scalar,
                                  set_dict)


class FilterB2CConfig(nparcel.B2CConfig):
    """:class:`nparcel.FilterB2CConfig` captures the configuration items
    required for the ``npfilterd`` facility.

    .. attribute:: filter_loop

        time (seconds) between filter processing iterations.

    .. attribute:: filters

        dictionary of Alternate Delivery Partner names and a list
        of tokens to match against the start of the agent code field

    """
    _filter_loop = 30
    _filters = {}

    @property
    def filter_loop(self):
        return self._filter_loop

    @set_scalar
    def set_filter_loop(self, value):
        pass

    @property
    def filters(self):
        return self._filters

    @set_dict
    def set_filters(self, value):
        pass

    def parse_config(self):
        """Read config items from the configuration file.

        """
        nparcel.Config.parse_config(self)

        kwargs = [{'section': 'files',
                   'option': 't1250_file_format'},
                  {'section': 'dirs',
                   'option': 'staging_base'},
                  {'section': 'email',
                   'option': 'support',
                   'var': 'support_emails',
                   'is_list': True},
                  {'section': 'timeout',
                   'option': 'filter_loop',
                   'cast_type': 'int'},
                  {'section': 'dirs',
                   'option': 'aggregator',
                   'var': 'aggregator_dirs',
                   'is_list': True,
                   'is_required': True}]
        for kw in kwargs:
            self.parse_scalar_config(**kw)

        self.parse_dict_config(section='filters', is_list=True)

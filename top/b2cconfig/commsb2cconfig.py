__all__ = [
    "CommsB2CConfig",
]
import top
from top.utils.log import log
from top.utils.setter import (set_scalar,
                              set_list)


class CommsB2CConfig(top.B2CConfig):
    """:class:`top.CommsB2CConfig` captures the configuration items
    required for the ``topcommsd`` facility.

    .. attribute:: *comms_loop*

        time (seconds) between comms notification iterations.

    .. attribute:: *comms_dir*

        directory where comms files are read from

    .. attribute:: *comms_q_warning*

        comms queue warning threshold.  If number of messages exceeds this
        threshold (and is under the :attr:`comms_q_error` threshold then a
        warning email notification is triggered

    .. attribute:: *comms_q_error*

        comms queue error threshold.  If number of messages exceeds this
        threshold then an error email notification is triggered and
        the comms daemon is terminated


    .. attribute:: *controlled_templates*

        list of comms templates that are controlled by the delivery
        period thresholds

    .. attribute:: *uncontrolled_templates*

        list of comms templates that are *NOT* controlled by the delivery
        period thresholds.  In other words, comms can be sent 24 x 7

    .. attribute:: *skip_days*

        list of days ['Saturday', 'Sunday'] to not send messages

    .. attribute:: *send_time_ranges*

        time ranges when comms can be sent

    """
    _comms_loop = 30
    _comms_dir = None
    _comms_q_warning = 100
    _comms_q_error = 1000
    _controlled_templates = []
    _uncontrolled_templates = []
    _skip_days = ['Sunday']
    _send_time_ranges = ['08:00-19:00']

    def __init__(self, file=None):
        """CommsB2CConfig initialisation.
        """
        top.B2CConfig.__init__(self, file)

    @property
    def comms_dir(self):
        return self._comms_dir

    @set_scalar
    def set_comms_dir(self, value):
        pass

    @property
    def comms_loop(self):
        return self._comms_loop

    @set_scalar
    def set_comms_loop(self, value):
        pass

    @property
    def comms_q_warning(self):
        return self._comms_q_warning

    @set_scalar
    def set_comms_q_warning(self, value):
        pass

    @property
    def comms_q_error(self):
        return self._comms_q_error

    @set_scalar
    def set_comms_q_error(self, value):
        pass

    @property
    def controlled_templates(self):
        return self._controlled_templates

    @set_list
    def set_controlled_templates(self, values=None):
        pass

    @property
    def uncontrolled_templates(self):
        return self._uncontrolled_templates

    @set_list
    def set_uncontrolled_templates(self, values=None):
        pass

    @property
    def skip_days(self):
        return self._skip_days

    @set_list
    def set_skip_days(self, values=None):
        pass

    @property
    def send_time_ranges(self):
        return self._send_time_ranges

    @set_list
    def set_send_time_ranges(self, values=None):
        pass

    def parse_config(self):
        """Read config items from the configuration file.

        """
        top.Config.parse_config(self)

        kwargs = [{'section': 'dirs',
                   'option': 'comms',
                   'var': 'comms_dir',
                   'is_required': True},
                  {'section': 'timeout',
                   'option': 'comms_loop',
                   'cast_type': 'int'},
                  {'section': 'comms',
                   'option': 'comms_queue_warning',
                   'var': 'comms_q_warning',
                   'cast_type': 'int'},
                  {'section': 'comms',
                   'option': 'comms_queue_error',
                   'var': 'comms_q_error',
                   'cast_type': 'int'},
                  {'section': 'comms',
                   'option': 'controlled_templates',
                   'is_list': True},
                  {'section': 'comms',
                   'option': 'uncontrolled_templates',
                   'is_list': True},
                  {'section': 'comms',
                   'option': 'skip_days',
                   'is_list': True},
                  {'section': 'comms',
                   'option': 'send_time_ranges',
                   'is_list': True}]
        for kw in kwargs:
            self.parse_scalar_config(**kw)

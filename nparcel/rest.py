__all__ = [
    "Rest",
]
import socket

from nparcel.utils.log import log


class Rest(object):
    """Nparcel REST-based class.

    .. attribute:: proxy

        proxy credentials that allow for HTTP* requests via a proxy

    .. attribute:: proxy_scheme

        The URI scheme for the proxy

    .. attribute:: api

        URI of the RESTful API to connect to

    .. attribute:: api_username

        username of the RESTful API

    .. attribute:: api_password

        password of the RESTful API

    .. attribute:: hostname

        string containing the hostname of the machine where the Python
        interpreter is currently executing

    """
    _facility = None

    def __init__(self,
                 proxy=None,
                 proxy_scheme='http',
                 api=None,
                 api_username=None,
                 api_password=None):
        """rest initialiser.

        """
        self._facility = self.__class__.__name__

        self._proxy = proxy
        self._proxy_scheme = proxy_scheme
        self._api = api
        self._api_username = api_username
        self._api_password = api_password

        self.set_hostname(socket.gethostname())

    @property
    def facility(self):
        return self._facility

    @property
    def proxy(self):
        return self._proxy

    def set_proxy(self, value):
        self._proxy = value
        log.debug('%s proxy set to "%s"' % (self.facility, self.proxy))

    @property
    def proxy_scheme(self):
        return self._proxy_scheme

    def set_proxy_scheme(self, value):
        self._proxy_scheme = value
        log.debug('%s proxy_scheme set to "%s"' %
                  (self.facility, self.proxy_scheme))

    @property
    def api(self):
        return self._api

    def set_api(self, value):
        self._api = value
        log.debug('%s api set to "%s"' % (self.facility, self.api))

    @property
    def api_username(self):
        return self._api_username

    def set_api_username(self, value):
        self._api_username = value
        log.debug('%s api set to "%s"' % (self.facility, self.api_username))

    @property
    def api_password(self):
        return self._api_password

    def set_api_password(self, value):
        self._api_password = value
        log.debug('%s api set to "********"' % self.facility)

    @property
    def hostname(self):
        return self._hostname

    def set_hostname(self, value):
        self._hostname = value
        log.debug('%s hostname set to "%s"' %
                  (self.facility, self.hostname))

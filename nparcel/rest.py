__all__ = [
    "Rest",
]
import re
import urllib
import nparcel.urllib2 as urllib2

from nparcel.utils.log import log


class Rest(object):
    """Nparcel REST-based class.

    .. attribute:: proxy

        proxy credentials that allow for HTTP* requests via a proxy

    .. attribute:: api

        URI of the RESTful API to connect to

    .. attribute:: api_username

        username of the RESTful API

    .. attribute:: api_password

        password of the RESTful API

    """

    def __init__(self,
                 proxy=None,
                 proxy_scheme='http',
                 api=None,
                 api_username=None,
                 api_password=None):
        """Nparcel REST initialiser.

        """
        self._proxy = proxy
        self._proxy_scheme = proxy_scheme
        self._api = api
        self._api_username = api_username
        self._api_password = api_password

    @property
    def proxy(self):
        return self._proxy

    def set_proxy(self, value):
        self._proxy = value

    @property
    def proxy_scheme(self):
        return self._proxy_scheme

    def set_proxy_scheme(self, value):
        self._proxy_scheme = value

    @property
    def api(self):
        return self._api

    def set_api(self, value):
        self._api = value

    @property
    def api_username(self):
        return self._api_username

    def set_api_username(self, value):
        self._api_username = value

    @property
    def api_password(self):
        return self._api_password

    def set_api_password(self, value):
        self._api_password = value

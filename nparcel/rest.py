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

    """

    def __init__(self,
                 proxy=None,
                 proxy_scheme='http',
                 api=None):
        """Nparcel REST initialiser.

        """
        self._proxy = proxy
        self._proxy_scheme = proxy_scheme
        self._api = api

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

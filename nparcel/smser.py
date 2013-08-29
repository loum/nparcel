__all__ = [
    "Smser",
]
import re
import urllib
import nparcel.urllib2 as urllib2

from nparcel.utils.log import log


class Smser(object):
    """Nparcel SMSer.

    .. attribute:: recipients

        list of mobile numbers to send SMS to

    .. attribute:: proxy

        proxy credentials that allow for HTTP* requests via a proxy

    .. attribute:: api

        URI of the RESTful API to connect to

    """

    def __init__(self,
                 recipients=None,
                 proxy=None,
                 proxy_scheme='http',
                 api=None):
        """Nparcel Smser initiliser.

        """
        if recipients is None:
            self._recipients = []
        else:
            self._recipients = recipients

        self._proxy = proxy
        self._proxy_scheme = proxy_scheme
        self._api = api

    @property
    def recipients(self):
        return self._recipients

    def set_recipients(self, values):
        del self._recipients[:]

        if values is not None:
            self._recipients.extend(values)

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

    def send(self, msg, dry=False):
        """Send the SMS.

        **Args:**
            subject: the email subject

            msg: sms message

        **Kwargs:**
            dry: do not send, only report what would happen

        """
        log.info('Sending SMS comms ...')
        status = True

        # Verify SMS recipients.
        if not len(self.recipients):
            log.warn('No SMS recipients provided')
            status = False

        if status:
            for recipient in self.recipients:
                if not self.validate(recipient):
                    status = False
                    break

        if self.api is None:
            log.error('No SMS API provided -- SMS not sent')
            status = False

        if status:
            for mobile in self.recipients:
                params = self.encode_params(msg, mobile)
                url = "%s?%s" % (self.api, params)
                log.debug('Generated SMS URL: %s' % url)
                if not dry:
                    proxy_kwargs = {}
                    if self.proxy is not None:
                        proxy_kwargs = {self.proxy_scheme: self.proxy}
                    proxy = urllib2.ProxyHandler(proxy_kwargs)
                    auth = urllib2.HTTPBasicAuthHandler()
                    opener = urllib2.build_opener(proxy,
                                                  auth,
                                                  urllib2.HTTPSHandler)
                    urllib2.install_opener(opener)

                    try:
                        conn = urllib2.urlopen(url)
                        response = conn.read()
                        log.info('SMS receive: "%s"' % response)
                    except urllib2.URLError, e:
                        log.warn('SMS failure: %s' % e)

        return status

    def encode_params(self, msg, mobile):
        """URL encode the message so that is is compatible with URL
        transmissions to the TextMagic API.

        **Args:**
            msg: the string to URL encode.

        **Returns:**
            the encoded string

        """
        f = {'username': 'lubster',
             'password': 'Nlj3hCb1PdsgoJZ',
             'cmd': 'send',
             'text': msg,
             'unicode': 0,
             'phone': mobile}
        #f = {'username': 'lubster',
        #     'password': 'Nlj3hCb1PdsgoJZ',
        #     'cmd': 'account'}
        encoded_msg = urllib.urlencode(f)

        return encoded_msg

    def validate(self, mobile_number):
        """Validate the *mobile_number*.

        Runs a few simple validation checks to ensure that the number is
        valid.  Checks include:

        * all numeric digits

        * length of 10

        * starts with '04'

        **Args:**
            mobile_number: the mobile number to validate

        **Returns:**
            boolean ``True`` if the number validates

            boolean ``False`` if the number fails

        """
        status = True

        err = 'Mobile "%s" validation failed: ' % mobile_number
        regex = re.compile("\d{10}$")
        m = regex.match(mobile_number)
        if m is None:
            status = False
            err += "not 10 digits"
            log.warn(err)

        if status:
            if mobile_number[0:2] != '04':
                status = False
                err += 'does not start with "04"'
                log.warn(err)

        return status

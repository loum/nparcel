__all__ = [
    "Smser",
]
import urllib
import nparcel.urllib2 as urllib2

from nparcel.utils.log import log


class Smser(object):
    """Nparcel SMSer.
    """

    def __init__(self, recipients=None):
        """Nparcel Smser initiliser.

        """
        if recipients is None:
            self._recipients = []
        else:
            self._recipients = recipients

    @property
    def recipients(self):
        return self._recipients

    def set_recipients(self, values):
        del self._recipients[:]

        if values is not None:
            self._recipients.extend(values)

    def send(self, msg, dry=False):
        """Send the SMS.

        **Args:**
            subject: the email subject

            msg: sms message

        **Kwargs:**
            dry: do not send, only report what would happen

        """
        status = True

        log.info('Sending SMS comms ...')
        if len(self.recipients):
            for mobile in self.recipients:
                params = self.encode_params(msg, mobile)
                api = 'https://www.textmagic.com/app/api'
                url = "%s?%s" % (api, params)
                log.debug('Generated SMS URL: %s' % url)
                if not dry:
                    proxy = {'user': 'loumar',
                             'pass': 'P0o9i8U7',
                             'host': 'auproxy-farm.toll.com.au',
                             'port': 8080}
                    proxy_str = "http://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy
                    proxy = urllib2.ProxyHandler({'https': proxy_str})
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
        else:
            log.warn('No SMS recipients provided')

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

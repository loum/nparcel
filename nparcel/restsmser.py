__all__ = [
    "RestSmser",
]
import re
import base64

import nparcel
import nparcel.urllib2 as urllib2
from nparcel.utils.log import log


class RestSmser(nparcel.Rest):
    """Nparcel RestSmser.

    """

    def __init__(self,
                 proxy=None,
                 proxy_scheme='http',
                 api=None,
                 api_username=None,
                 api_password=None):
        """Nparcel Smser initialiser.

        """
        super(RestSmser, self).__init__(proxy,
                                        proxy_scheme,
                                        api,
                                        api_username,
                                        api_password)

    def send(self, data, dry=False):
        """Send the SMS.

        **Args:**
            data: XML construct that contains the sms message details

        **Kwargs:**
            dry: do not send, only report what would happen

        """
        log.info('Sending SMS comms ...')
        status = True

        if self.api is None:
            log.error('No SMS API provided -- SMS not sent')
            status = False

        if status:
            log.debug('REST SMS data: %s' % data)
            proxy_kwargs = {}
            if self.proxy is not None:
                proxy_kwargs = {self.proxy_scheme: self.proxy}
            proxy = urllib2.ProxyHandler(proxy_kwargs)
            auth = urllib2.HTTPBasicAuthHandler()
            opener = urllib2.build_opener(proxy,
                                          auth,
                                          urllib2.HTTPSHandler)
            urllib2.install_opener(opener)

            log.debug('Preparing request to API: "%s"' % self.api)
            hdr = {'Content-Type': 'application/xml'}
            req = urllib2.Request(self.api, data, headers=hdr)
            b64str = base64.encodestring('%s:%s' %
                                         (self._api_username,
                                          self._api_password))
            req.add_header("Authorization",
                           "Basic %s" % b64str.replace('\n', ''))

            if not dry:
                try:
                    conn = urllib2.urlopen(req)
                    response = conn.read()
                    log.info('SMS receive: "%s"' % response)
                except urllib2.URLError, e:
                    log.warn('SMS failure: %s' % e)

        return status

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

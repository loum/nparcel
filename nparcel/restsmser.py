__all__ = [
    "RestSmser",
]
import re
import os
import string
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

    def create_comms(self, data, base_dir=None):
        """Create the SMS data string to send.

        **Args:**
            data: dictionary structure of items to expected by the HTML
            email templates::

               {'name': 'Auburn Newsagency',
                'address': '119 Auburn Road',
                'suburb': 'HAWTHORN EAST',
                'postcode': '3123',
                'item_nbr': '3456789012-item_nbr',
                'mobile': '0419368910'}

        **Kwargs:**
            base_dir: override the standard location to search for the
            SMS XML template (default ``~user_home/.nparceld/templates``).

        """
        dir = None
        if base_dir is None:
            dir = os.path.join(os.path.expanduser('~'),
                               '.nparceld',
                               'templates')
        else:
            dir = os.path.join(base_dir, 'templates')
        log.debug('SMS template dir: "%s"' % dir)

        sms_data = None
        try:
            xml_file = os.path.join(dir, 'sms_xml.t')
            f = open(xml_file)
            sms_t = f.read()
            f.close()
            sms_s = string.Template(sms_t)
            sms_data = sms_s.substitute(**data)
        except IOError, err:
            log.error('Unable to source SMS template at "%s"' % xml_file)

        return sms_data

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
            log.debug('proxy_scheme: %s' % self.proxy_scheme)
            log.debug('proxy: %s' % self.proxy)
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
            log.debug('SMS API username: "%s"' % self._api_username)
            if self._api_password:
                log.debug('SMS API password: "********"')
            else:
                log.debug('SMS API password undefined')
            req.add_header("Authorization",
                           "Basic %s" % b64str.replace('\n', ''))

            if not dry:
                try:
                    conn = urllib2.urlopen(req)
                    if conn.code != 200:
                        log.error('SMS comms return code: %d' % conn.code)
                        status = False
                    response = conn.read()
                    log.info('SMS receive: "%s"' % response)
                except urllib2.URLError, e:
                    log.warn('SMS failure: %s' % e)
                    status = False

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

__all__ = [
    "RestSmser",
]
import re
import os
import base64
from elementtree import ElementTree

import top
import top.urllib2 as urllib2
from top.utils.log import log
from top.utils.files import templater


class RestSmser(top.Rest):
    """RestSmser.

    .. attribute:: template_base
        directory where templates are read from

    """
    _facility = None
    _template_base = os.path.join(os.path.expanduser('~'),
                                  '.top',
                                  'templates')

    def __init__(self,
                 proxy=None,
                 proxy_scheme='http',
                 api=None,
                 api_username=None,
                 api_password=None):
        """Smser initialiser.

        """
        top.Rest.__init__(self,
                          proxy,
                          proxy_scheme,
                          api,
                          api_username,
                          api_password)

    @property
    def template_base(self):
        return self._template_base

    def set_template_base(self, value):
        self._template_base = value
        log.debug('%s template_base set to "%s"' %
                  (self._facility, self.template_base))

    def create_comms(self,
                     data,
                     template='body',
                     base_dir=None,
                     prod=None):
        """Create the SMS data string to send based on *data* and
        *template*.

        If current hostname matches *prod* then comms messages will be
        prepended with a special ``TEST ONLY`` descriptor.

        **Args:**
            *data*: dictionary structure of items to expected by the HTML
            email templates::

               {'name': 'Auburn Newsagency',
                'address': '119 Auburn Road',
                'suburb': 'HAWTHORN EAST',
                'postcode': '3123',
                'item_nbr': '3456789012-item_nbr',
                'phone_nbr': '0431602145'}

        **Kwargs:**
            *template*: template token that defines the message context.
            For example, ``ret`` for the returns template

            *base_dir*: override the standard location to search for the
            SMS XML template (default ``~user_home/.top/templates``).

            *prod*: hostname of the production instance machine

        **Returns:**
            string representation of the message to send or ``None`` if
            the template processing failed

        """
        template_dir = self.template_base
        if base_dir is not None:
            template_dir = base_dir

        # Add TEST token to message if not production.
        non_prod_string = None
        if prod != self.hostname:
            non_prod_template_file = os.path.join(template_dir,
                                                  'sms_non_prod.t')
            non_prod_string = templater(non_prod_template_file)
        if non_prod_string is None:
            non_prod_string = str()
        data['non_prod'] = non_prod_string

        sms_data = None
        path_to_template = os.path.join(template_dir,
                                        'sms_%s_xml.t' % template)
        sms_xml = templater(path_to_template, **data)

        return sms_xml

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
                    log.error('SMS failure: %s' % e)
                    status = False

        return status

    def validate(self, mobile_number):
        """Validate the *mobile_number*.

        Runs a few simple validation checks to ensure that the number is
        valid.  Checks include:

        * all numeric digits

        * length of 10

        * starts with '04'

        .. note::

            a 9-digit number with leading ``4`` will have a ``0``
            prepended to complete a valid mobile number construct.

        **Args:**
            *mobile_number*: the mobile number to validate

        **Returns:**
            boolean ``True`` if the number validates

            boolean ``False`` if the number fails

        """
        status = True

        tmp_mobile = self.check_mobile_missing_leading_zero(mobile_number)

        err = 'Mobile "%s" validation failed: ' % tmp_mobile
        regex = re.compile("\d{10}$")
        m = regex.match(tmp_mobile)
        if m is None:
            status = False
            err += "not 10 digits"
            log.info(err)

        if status:
            if tmp_mobile[0:2] != '04':
                status = False
                err += 'does not start with "04"'
                log.info(err)

        return status

    def check_mobile_missing_leading_zero(self, mobile_number):
        """Checks for a special case where the *mobile_number* number could
        have the leading ``0`` missing.

        The general algorithm is that a 9-digit *mobile_number*  with
        leading ``4`` will have a ``0`` prepended to complete a valid
        mobile number construct.

        **Args:**
            mobile_number: the mobile number to validate

        **Returns:**
            The transposed mobile number if the leading ``0`` scenario is
            encounterd.  Otherwise, the original value of *mobile_number*.

        """
        tmp_mobile_number = mobile_number

        regex = re.compile("\d{9}$")
        m = regex.match(mobile_number)
        if m is not None:
            if mobile_number[0] == '4':
                tmp_mobile_number = '0%s' % mobile_number
                log.info('Prepended "0" to mobile "%s" to produce "%s"' %
                         (mobile_number, tmp_mobile_number))

        return tmp_mobile_number

    def add_test_string(self, xml_message):
        """Add TEST token to the SMS XML message construct.

        **Args**:
            *xml_message*: the source XML message string to alter

        **Returns**:
            the altered SMS message as a string

        """
        log.debug('Adding TEST token to XML: "%s"' % xml_message)

        content = ElementTree.fromstring(xml_message)
        body = content.find('message/body')
        body.text = '%s\n%s' % ('TEST PLS IGNORE', body.text)

        new_xml_message = ElementTree.tostring(content, encoding='UTF-8')
        log.debug('New XML: "%s"' % new_xml_message)

        return new_xml_message

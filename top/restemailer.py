__all__ = [
    "RestEmailer",
]
import urllib

import nparcel
import nparcel.urllib2 as urllib2
from nparcel.utils.log import log


class RestEmailer(nparcel.Emailer):
    """RestEmailer class.

    """

    def __init__(self,
                 sender='no-reply@consumerdelivery.tollgroup.com',
                 recipients=None,
                 proxy=None,
                 proxy_scheme='http',
                 api=None,
                 api_username=None,
                 api_password=None,
                 support=None):
        """RestEmailer initialiser.

        """
        nparcel.Emailer.__init__(self, sender, recipients)
        self._rest = nparcel.Rest(proxy,
                                  proxy_scheme,
                                  api,
                                  api_username,
                                  api_password)

        if support is None:
            self._support = []
        else:
            self._support = support.split(',')

    @property
    def sender(self):
        return self._sender

    def set_sender(self, value):
        self._sender = value

    @property
    def support(self):
        return self._support

    def set_support(self, value):
        self._support = value.split(',')

    def encode_params(self,
                      subject,
                      sender,
                      recipient,
                      msg):
        """URL encode the message so that is is compatible with REST-based
        communications.

        **Args:**
            subject: email subject string

            username: username credential required by the RESTFul API

            passwd: password credential required by the RESTFul API

            sender: the sender of the email

            recipient: the recipient of the email

            msg: the email message body

        **Returns:**
            the encoded string

        """
        msg_preamble = ('%s\\n%s\\n%s' %
                        ('Content-Type: text/plain; charset="us-ascii"',
                         'MIME-Version: 1.0',
                         'Content-Transfer-Encoding: 7bit'))
        msg = ("%s\\nSubject: %s\\nFrom: %s\\nTo: %s\\n\\n%s" %
               (msg_preamble, subject, sender, recipient, msg))
        f = [('username', self._rest.api_username),
             ('password', self._rest.api_password),
             ('message', msg)]
        encoded_msg = urllib.urlencode(f)

        return encoded_msg

    def send_simple(self, subject, sender, recipient, msg, dry=False):
        """Send the Email.

        **Args:**
            *subject*: email subject

            *sender*: email sender (From)

            *recipient*: email recipient (To)

            *msg*: email content

        **Kwargs:**
            *dry*: do not send, only report what would happen

        **Returns:**
            boolean ``True`` if the send is successful

            boolean ``False`` if the send fails

        """
        log.info('Sending REST-based e-mail comms ...')
        status = True

        data = self.encode_params(subject=subject,
                                  sender=sender,
                                  recipient=recipient,
                                  msg=msg)

        proxy_kwargs = {}
        if self._rest.proxy is not None:
            proxy_kwargs = {self._rest.proxy_scheme: self.proxy}
        proxy = urllib2.ProxyHandler(proxy_kwargs)
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy,
                                      auth,
                                      urllib2.HTTPSHandler)
        urllib2.install_opener(opener)

        req = urllib2.Request(self._rest.api, data, {})
        if not dry:
            try:
                conn = urllib2.urlopen(req)
                if conn.code != 200:
                    log.error('Email comms return code: %d' % conn.code)
                    status = False
                response = conn.read()
                log.info('Email receive: "%s"' % response)
            except urllib2.URLError, e:
                status = False
                log.warn('Email failure: %s' % e)

        return status

    def check_subject(self, subject, prod):
        """Checks if current hostname matches *prod*.  If so, subject line
        is prepended with a special ``TEST ONLY`` descriptor.

        **Args:**
            *subject*: the email subject

            *prod*: hostname of the production instance machine

        **Returns:**

            subject line string based on context of PROD instance

        """
        new_subject = subject

        if prod is None or prod != self.hostname:
            new_subject = 'TEST PLEASE IGNORE -- %s' % subject
            log.debug('Added TEST token to subject: "%s"' % new_subject)

        return new_subject

    def send(self, data, dry=False):
        """Send the *data*.

        Performs a simple validation check of the recipients and will
        only send the email if all are OK.

        Empty recipient lists are ignored and no email send attempt is made.

        **Args:**
            data: POST message construct

        **Kwargs:**
            dry: do not send, only report what would happen

        """
        log.info('Sending REST-based e-mail comms ...')
        status = True

        if self._rest.api is None:
            log.error('No email API provided -- email not sent')
            status = False

        if not len(self.recipients):
            log.warn('No email recipients provided')
            status = False

        if status:
            for recipient in self.recipients:
                if not self.validate(recipient):
                    status = False
                    break

        if status:
            log.debug('Email API username: "%s"' % self._rest._api_username)
            if self._rest.api_password:
                log.debug('Email API username: "********"')
            else:
                log.debug('Email API username undefined')

            f = [('username', self._rest.api_username),
                 ('password', self._rest.api_password),
                 ('message', data)]
            encoded_msg = urllib.urlencode(f)

            proxy_kwargs = {}
            if self._rest.proxy is not None:
                proxy_kwargs = {self._rest.proxy_scheme: self._rest.proxy}
            log.debug('proxy_scheme: %s' % self._rest.proxy_scheme)
            log.debug('proxy: %s' % self._rest.proxy)
            proxy = urllib2.ProxyHandler(proxy_kwargs)
            auth = urllib2.HTTPBasicAuthHandler()
            opener = urllib2.build_opener(proxy,
                                          auth,
                                          urllib2.HTTPSHandler)
            urllib2.install_opener(opener)

            log.debug('Preparing request to API: "%s"' % self._rest.api)
            req = urllib2.Request(self._rest.api, encoded_msg, {})
            if not dry:
                try:
                    conn = urllib2.urlopen(req)
                    response = conn.read()
                    log.info('Email receive: "%s"' % response)
                except urllib2.URLError, e:
                    status = False
                    log.error('Email failure: %s' % e)

        return status

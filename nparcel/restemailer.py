__all__ = [
    "RestEmailer",
]
import urllib

import nparcel
import nparcel.urllib2 as urllib2
from nparcel.utils.log import log


class RestEmailer(nparcel.Rest):
    """Nparcel RestEmailer.

    """

    def __init__(self,
                 recipients=None,
                 proxy=None,
                 proxy_scheme='http',
                 api=None,
                 api_username=None,
                 api_password=None):
        """Nparcel RestEmailer initialiser.
        """
        super(RestEmailer, self).__init__(proxy,
                                          proxy_scheme,
                                          api,
                                          api_username,
                                          api_password)

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
        f = [('username', self.api_username),
             ('password', self.api_password),
             ('message', msg)]
        encoded_msg = urllib.urlencode(f)

        return encoded_msg

    def send(self, subject, sender, recipient, msg, dry=False):
        """Send the Email.

        **Args:**
            subject: email subject

            sender: email sender (From)

            recipient: email recipient (To)

            msg: email content

        **Kwargs:** 
            dry: do not send, only report what would happen

        **Returns:**
            boolean ``True`` if the send is successful

            boolean ``False`` if the send fails

        """
        status = True

        data = self.encode_params(subject=subject,
                                  sender=sender,
                                  recipient=recipient,
                                  msg=msg)

        proxy_kwargs = {}
        if self.proxy is not None:
            proxy_kwargs = {self.proxy_scheme: self.proxy}
        proxy = urllib2.ProxyHandler(proxy_kwargs)
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy,
                                      auth,
                                      urllib2.HTTPSHandler)
        urllib2.install_opener(opener)

        req = urllib2.Request(self.api, data, {})
        if not dry:
            try:
                conn = urllib2.urlopen(req)
                response = conn.read()
                log.info('Email receive: "%s"' % response)
            except urllib2.URLError, e:
                status = False
                log.warn('Email failure: %s' % e)

        return status

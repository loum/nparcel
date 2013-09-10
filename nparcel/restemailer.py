__all__ = [
    "RestEmailer",
]
import re
import urllib
import string
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
import getpass
import socket

import nparcel
import nparcel.urllib2 as urllib2
from nparcel.utils.log import log


class RestEmailer(nparcel.Rest):
    """Nparcel RestEmailer.

    .. attribute:: recipients

        list of mobile numbers to send SMS to

    """

    def __init__(self,
                 sender=None,
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

        self._sender = sender
        if self._sender is None:
            self._sender = "%s@%s" % (getpass.getuser(), socket.getfqdn())
            log.debug('Set sender as "%s"' % self._sender)

        if recipients is None:
            self._recipients = []
        else:
            self._recipients = recipients

    @property
    def sender(self):
        return self._sender

    def set_sender(self, value):
        self._sender = value

    @property
    def recipients(self):
        return self._recipients

    def set_recipients(self, values):
        del self._recipients[:]

        if values is not None:
            self._recipients.extend(values)

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

    def create_comms(self, subject, data):
        """Create the MIME multipart message that can feed directly into
        the POST construct of the Esendex RESTful API.

        **Args:**
            subject: the email subject

            data: dictionary structure of items to expected by the HTML
            email templates::

                {'name': 'Auburn Newsagency',
                 'address': '119 Auburn Road',
                 'suburb': 'HAWTHORN EAST',
                 'postcode': '3123',
                 'barcode': '218501217863-barcode',
                 'item_nbr': '3456789012-item_nbr'}

        **Returns:**
            MIME multipart-formatted serialised string

        """
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = subject
        mime_msg['From'] = self.sender
        mime_msg['To'] = ", ".join(self.recipients)

        msgAlternative = MIMEMultipart('alternative')
        mime_msg.attach(msgAlternative)

        f = open('nparcel/templates/email_body_html.t')
        body_t = f.read()
        f.close()
        body_s = string.Template(body_t)
        body = body_s.substitute(**data)

        f = open('nparcel/templates/email_html.t')
        main_t = f.read()
        f.close()
        main_s = string.Template(main_t)
        main = main_s.substitute(body=body)

        main_text = MIMEText(main, 'html')
        msgAlternative.attach(main_text)

        f = open('nparcel/images/toll_logo.png')
        msgImage = MIMEImage(f.read(), 'rb')
        f.close()
        msgImage.add_header('Content-ID', '<toll_logo>')
        mime_msg.attach(msgImage)

        f = open('nparcel/images/nparcel_logo.png')
        msgImage = MIMEImage(f.read(), 'rb')
        f.close()
        msgImage.add_header('Content-ID', '<nparcel_logo>')
        mime_msg.attach(msgImage)

        return mime_msg.as_string()

    def xxx(self, data, dry=False):
        """Send the *msg*.

        Performs a simple validation check of the recipients and will
        only send the email if all are OK.

        Empty recipient lists are ignored and no email send attempt is made.

        **Args:**
            subject: the email subject

            data: POST message construct

        **Kwargs:**
            dry: do not send, only report what would happen

        """
        log.info('Sending email comms ...')
        status = True

        # Verify email addresses.
        if not len(self.recipients):
            log.warn('No email recipients provided')
            status = False

        if status:
            for recipient in self.recipients:
                if not self.validate(recipient):
                    status = False
                    break

        if status:
            f = [('username', self.api_username),
                 ('password', self.api_password),
                 ('message', data)]
            encoded_msg = urllib.urlencode(f)

            proxy_kwargs = {}
            if self.proxy is not None:
                proxy_kwargs = {self.proxy_scheme: self.proxy}
            proxy = urllib2.ProxyHandler(proxy_kwargs)
            auth = urllib2.HTTPBasicAuthHandler()
            opener = urllib2.build_opener(proxy,
                                          auth,
                                          urllib2.HTTPSHandler)
            urllib2.install_opener(opener)

            req = urllib2.Request(self.api, encoded_msg, {})
            if not dry:
                try:
                    conn = urllib2.urlopen(req)
                    response = conn.read()
                    log.info('Email receive: "%s"' % response)
                except urllib2.URLError, e:
                    status = False
                    log.warn('Email failure: %s' % e)

        return status

    def validate(self, email):
        """Validate the *email* address.

        Runs a simple regex validation across the *email* address is

        **Args:**
            email: the email address to validate

        **Returns:**
            boolean ``True`` if the email validates

            boolean ``False`` if the email does not validate

        """
        status = True

        err = 'Email "%s" validation failed' % email
        r = re.compile("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$")
        m = r.match(email)
        if m is None:
            status = False
            log.error(err)

        return status

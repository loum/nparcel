__all__ = [
    "RestEmailer",
]
import os
import urllib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import getpass
import socket

import nparcel
import nparcel.urllib2 as urllib2
from nparcel.utils.log import log
from nparcel.utils.files import templater


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
        nparcel.Emailer.__init__(self)

        self._rest = nparcel.Rest(proxy,
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
    def recipients(self):
        return self._recipients

    def set_recipients(self, values):
        del self._recipients[:]

        if values is not None:
            self._recipients.extend(values)

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
        log.info('Sending email comms ...')
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

    def create_comms(self,
                     data,
                     base_dir=None,
                     template='body',
                     err=False,
                     prod=None):
        """Create the MIME multipart message that can feed directly into
        the POST construct of the Esendex RESTful API.

        If current hostname matches *prod* then comms messages will be
        prepended with a special ``TEST ONLY`` descriptor.

        **Args:**
            *data*: dictionary structure of items to expected by the HTML
            email templates::

                {'name': 'Auburn Newsagency',
                 'address': '119 Auburn Road',
                 'suburb': 'HAWTHORN EAST',
                 'postcode': '3123',
                 'barcode': '218501217863-barcode',
                 'item_nbr': '3456789012-item_nbr'}

        **Kwargs:**
            *base_dir*: override the standard location to search for the
            templates (default ``~user_home/.nparceld/templates``).

            *prod*: hostname of the production instance machine

        **Returns:**
            MIME multipart-formatted serialised string

        """
        template_dir = self.template_base
        if base_dir is not None:
            template_dir = base_dir

        # Subject.
        subject = self.get_subject_line(data,
                                        template=template,
                                        err=err)
        if subject is None:
            log.error('Subject email could not be generated')
            subject = str()

        mime_msg = MIMEMultipart('related')
        mime_msg['From'] = self.sender
        mime_msg['To'] = ", ".join(self.recipients)
        mime_msg['Subject'] = self.check_subject(subject, prod)

        msgAlternative = MIMEMultipart('alternative')
        mime_msg.attach(msgAlternative)

        err_html = None
        if err:
            path_to_err_template = os.path.join(template_dir, 'err_html.t')
            err_html = templater(path_to_err_template, **data)

        if err_html is None:
            err_html = str()
        data['err'] = err_html

        non_prod_html = None
        if prod != self.hostname:
            path_to_non_prod_template = os.path.join(template_dir,
                                                     'email_non_prod_html.t')
            non_prod_html = templater(path_to_non_prod_template, **data)

        if non_prod_html is None:
            non_prod_html = str()
        data['non_prod'] = non_prod_html

        # Build the email body portion.
        html_body_template = 'email_%s_html.t' % template
        path_to_template = os.path.join(template_dir, html_body_template)
        body_html = templater(path_to_template, **data)

        # Plug the body into the main HTML container.
        main_html = None
        if body_html is not None:
            path_to_main_template = os.path.join(template_dir,
                                                 'email_html.t')
            main_html = templater(path_to_main_template, body=body_html)

        # Build the MIME message.
        mime_msg_string = None
        if main_html is not None:
            mime_text = MIMEText(main_html, 'html')
            msgAlternative.attach(mime_text)
            mime_msg_string = mime_msg.as_string()

        log.debug('Complete Mime message: "%s"' % mime_msg_string)

        return mime_msg_string

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
        log.info('Sending email comms ...')
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

    def get_subject_line(self,
                         data,
                         base_dir=None,
                         template='body',
                         err=False):
        """Construct email subject line from a template.

        **Args**:
            *data*: dictionary structure that features the tokens that feed
            into the template

        **Kwargs**:
            *base_dir*: override the :attr:`template_dir`

            *template*: template file that contains the subject line
            construct

            *err*: message context is for error comms

        **Returns**:
            string representation of the subject

        """
        template_dir = self.template_base
        if base_dir is not None:
            template_dir = base_dir

        # Check if this is error context.
        err_string = None
        if err:
            log.debug('Altering subject line to error context ...')
            err_template_file = os.path.join(template_dir, 'subject_err.t')
            err_string = templater(err_template_file)
            if err_string is not None:
                err_string.rstrip()

        if err_string is None:
            err_string = str()
        data['err'] = err_string

        subject_html = 'subject_%s_html.t' % template
        subject_template_file = os.path.join(template_dir, subject_html)
        subject = templater(subject_template_file, **data)

        if subject is not None:
            subject = subject.rstrip()

        return subject

__all__ = [
    "Emailer",
]
import os
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
import getpass
from socket import gaierror, getfqdn

import nparcel
from nparcel.utils.log import log
from nparcel.utils.files import templater


class Emailer(nparcel.EmailerBase):
    """Emailer class.

    .. attribute:: sender

        email address of sending entity.  Value can be overridden with
        attribute setter.  Otherwise, defaults to current login during
        class initialisation

    .. attribute:: recipients

        list of email addressed to send e-mail to

    """
    _sender = None
    _recipients = []

    def __init__(self,
                 sender=None,
                 recipients=None):
        """Emailer initialiser.

        """
        nparcel.EmailerBase.__init__(self)

        self._sender = sender
        if self._sender is None:
            self._sender = "%s@%s" % (getpass.getuser(), getfqdn())

        if recipients is None:
            self._recipients = []
        else:
            self._recipients = recipients

    @property
    def sender(self):
        return self._sender

    def set_sender(self, value):
        self._sender = value
        log.debug('%s sender set to "%s"' % (self.facility, self.sender))

    @property
    def recipients(self):
        return self._recipients

    def set_recipients(self, values=None):
        del self._recipients[:]
        self._recipients = []

        if values is not None:
            self._recipients.extend(values)
            log.debug('%s recipients set to: "%s" ' %
                      (self.facility, self.recipients))

    def send(self, subject=None, msg=None, mime_message=None, dry=False):
        """Send the *msg* or *mime_message*.

        Performs a simple validation check of the recipients and will
        only send the email if all are OK.

        Empty recipient lists are ignored and no email send attempt is made.

        **Kwargs:**
            *subject*: override the email subject (*msg* based)

            *msg*: simple text-based email message

            *mime_message*: MIME-based email structure that includes
            the subject and recipients

            *dry*: do not send, only report what would happen

        .. note::

            *mime_message* will override the *subject* and *msg*.  No
            attempt is made to validate the structure of the MIME message.

        """
        log.info('Sending SMTP e-mail comms ...')
        status = True

        # Verify email addresses.
        if not len(self.recipients):
            log.error('No email recipients provided')
            status = False

        if status:
            for recipient in self.recipients:
                if not self.validate(recipient):
                    status = False
                    break

        if status:
            # OK, send the message.
            content = mime_message
            if content is None:
                if subject is None:
                    subject = str()
                mime_msg = MIMEText(msg)
                mime_msg['Subject'] = subject
                mime_msg['From'] = self.sender
                mime_msg['To'] = ", ".join(self.recipients)
                content = mime_msg.as_string()

            # ... and send.
            log.info('Sending email to recipients: "%s"' %
                     str(self.recipients))

            s = None
            if not dry:
                try:
                    s = smtplib.SMTP()
                except gaierror, err:
                    status = False
                    log.error('Could not connect to SMTP server "%s"' % err)

            if s is not None:
                s.connect()
                try:
                    s.sendmail(self.sender, self.recipients, content)
                except (smtplib.SMTPRecipientsRefused,
                        smtplib.SMTPHeloError,
                        smtplib.SMTPSenderRefused,
                        smtplib.SMTPDataError), err:
                    status = False
                    log.error('Could not send email: %s' % err)
                s.close()

        return status

    def create_comms(self,
                     data,
                     base_dir=None,
                     subject=None,
                     template='body',
                     files=None,
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

            *files*: list of files to send as an attachment

            *err*: email message error context flag.  If ``True``, context
            is error-based

            *prod*: hostname of the production instance machine

        **Returns:**
            MIME multipart-formatted serialised string

        """
        template_dir = self.template_base
        if base_dir is not None:
            template_dir = base_dir

        # Subject.
        if subject is None:
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

        # Attach files.
        if files is not None:
            for f in files:
                log.debug('Attaching file: "%s"' % f)
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(f, "rb").read())
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                'attachment; filename="%s"' %
                                os.path.basename(f))
                msgAlternative.attach(part)

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

        log.debug('Complete MIME message: "%s"' % mime_msg_string)

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

        if err_string is None:
            err_string = str()
        data['err'] = err_string

        subject_html = 'subject_%s_html.t' % template
        subject_template_file = os.path.join(template_dir, subject_html)
        subject = templater(subject_template_file, **data)

        return subject

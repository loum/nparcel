__all__ = [
    "Emailer",
]
import re
import smtplib
from email.MIMEText import MIMEText
import getpass
from socket import gaierror, getfqdn

from nparcel.utils.log import log


class Emailer(object):
    """Nparcel emailer.
    """

    def __init__(self,
                 sender=None,
                 recipients=None):
        """Nparcel emailer initialiser.

        """
        self._sender = sender
        if self.sender is None:
            sender = "%s@%s" % (getpass.getuser(), getfqdn())
            log.debug('Setting sender as "%s"' % sender)
            self.set_sender(sender)

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

    def send(self, subject, msg, dry=False):
        """Send the *msg*.

        Performs a simple validation check of the recipients and will
        only send the email if all are OK.

        Empty recipient lists are ignored and no email send attempt is made.

        **Args:**
            subject: the email subject

            msg: email message

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
            # OK, send the message.
            mime_msg = MIMEText(msg)
            mime_msg['Subject'] = subject
            mime_msg['From'] = self.sender
            mime_msg['To'] = ", ".join(self.recipients)

            # ... and send.
            s = None
            if not dry:
                try:
                    s = smtplib.SMTP()
                except gaierror, err:
                    status = False
                    log.error('Could not connect to SMTP server "%s"' % err)

            if s is not None:
                s.connect()
                log.info('Sending email to recipients: "%s"' %
                         str(self.recipients))
                try:
                    s.sendmail(self.sender,
                               self.recipients,
                               mime_msg.as_string())
                except (smtplib.SMTPRecipientsRefused,
                        smtplib.SMTPHeloError,
                        smtplib.SMTPSenderRefused,
                        smtplib.SMTPDataError), err:
                    status = False
                    log.warn('Could not send email: %s' % err)
                s.close()

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

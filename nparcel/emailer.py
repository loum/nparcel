__all__ = [
    "Emailer",
]
import smtplib
from email.MIMEText import MIMEText
import getpass
from socket import gaierror

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
        if values is None:
            del self._recipients[:]
        else:
            self._recipients.append(values)

    def send(self, subject, msg, dry=False):
        """Send the *msg*.

        Will try to source the sender as specified in the *sender*
        attribute.  Otherwise, sender will be determined automatically
        as the current user.

        **Args:**
            subject: the email subject

            msg: email message

        **Kwargs:**
            dry: do not send, only report what would happen

        """
        if not self.recipients:
            log.warn('No email recipients provided')
            raise TypeError('No recipients provided')

        if self.sender is None:
            sender = getpass.getuser()
            log.debug('Setting sender as "%s"' % sender)
            self.set_sender(sender)

        # OK, send the message.
        mime_msg = MIMEText(msg)
        mime_msg['Subject'] = subject
        mime_msg['From'] = self.sender
        mime_msg['To'] = self.recipients

        # ... and send.
        s = None
        if not dry:
            try:
                s = smtplib.SMTP()
            except gaierror, err:
                log.error('Could not connect to SMTP server "%s"' % err)

        if s is not None:
            s.connect()
            log.info('Sending email to recipients: "%s"' %
                     str(self.recipients))
            s.sendmail(self.sender, self.recipients, mime_msg.as_string())
            s.close()

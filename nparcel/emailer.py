__all__ = [
    "Emailer",
]
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

        Will try to source the sender as specified in the *sender*
        attribute.  Otherwise, sender will be determined automatically
        as the current user.

        **Args:**
            subject: the email subject

            msg: email message

        **Kwargs:**
            dry: do not send, only report what would happen

        """
        status = True

        log.info('Sending email comms ...')
        if len(self.recipients):
            if self.sender is None:
                sender = "%s@%s" % (getpass.getuser(), getfqdn())
                log.debug('Setting sender as "%s"' % sender)
                self.set_sender(sender)

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
                    pass

            if s is not None:
                s.connect()
                log.info('Sending email to recipients: "%s"' %
                         str(self.recipients))
                s.sendmail(self.sender,
                           self.recipients,
                           mime_msg.as_string())
                s.close()
        else:
            log.warn('No email recipients provided')

        return status

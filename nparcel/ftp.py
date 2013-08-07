__all__ = [
    "Ftp",
]
import ftplib
import nparcel


class Ftp(ftplib.FTP):
    """Nparcel FTP client.
    """

    def __init__(self):
        """Nparcel Ftp initialisation.
        """
        ftplib.FTP.__init__(self)

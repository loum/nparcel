__all__ = [
    "Auditer",
]
import datetime

import nparcel
from nparcel.utils.log import log
from nparcel.utils import date_diff


class Auditer(nparcel.Service):
    """Toll Parcel Portal base Auditer class.

    .. attribute::
        *bu_id*: dictionary mapping between Business Unit ID (``job.bu_id``
        column) and a human-readable format.  The default is::

            {1: 'Toll Priority',
             2: 'Toll Fast',
             3: 'Toll IPEC'}

    """
    _bu_ids = {}

    def __init__(self, db_kwargs=None, bu_ids=None):
        """Auditer initialiser.

        """
        if bu_ids is not None:
            self._bu_ids = bu_ids

        super(nparcel.Auditer, self).__init__(db=db_kwargs)

    @property
    def bu_ids(self):
        return self._bu_ids

    def set_bu_ids(self, values):
        self._bu_ids.clear()

        if values is not None:
            self._bu_ids = values
            log.debug('Set bu_ids to "%s"' % self._bu_ids)
        else:
            log.debug('Cleared bu_ids')

    def _translate_bu(self, headers, row, bu_ids):
        """Translate the BU ID to the Business Unit name string.

        **Args:**
            *header*: list of column headers

            *row*: tuple structure that represents the raw row result

            *bu_ids*: dictionary mapping between Business Unit ID
            (``job.bu_id`` column) and a human-readable format.  Example::

                {1: 'Toll Priority',
                 2: 'Toll Fast',
                 3: 'Toll IPEC'}

        **Returns:**
            the altered *row* tuple structure

        """
        tmp_row_list = list(row)

        index = None
        try:
            index = headers.index('JOB_BU_ID')
        except ValueError, err:
            log.warn('No "JOB_BU_ID" column in headers')

        if index is not None:
            orig_value = row[index]
            translated_bu = bu_ids.get(orig_value)
            if translated_bu is not None:
                tmp_row_list[index] = bu_ids.get(orig_value)
                log.debug('Translated BU ID "%s" to "%s"' % (orig_value,
                                                             translated_bu))
            else:
                log.debug('Unable to translate BU for "%s"' % orig_value)

        return tuple(tmp_row_list)

    def add_date_diff(self,
                      headers,
                      row,
                      time_column='JOB_TS',
                      time_to_compare=None):
        """Calculate the date delta between the value in the *time_column*
        and *time_to_compare*.

        Time delta will eventually be appended to the *row* tuple and
        returned to the caller.

        **Args:**
            *header*: list of column headers

            *row*: tuple structure that represents the raw row result

            *time_column*: column header to use in the time
            comparison

        **Kwargs:**
            *time_to_compare*: time to compare against (default ``None``
            in which time current time is used)

        **Returns:**
            the altered *row* tuple structure with new date delta
            value appended (if *time_column* exists)

        """
        tmp_row_list = list(row)

        index = None
        try:
            index = headers.index(time_column)
        except ValueError, err:
            log.warn('No "%s" column in headers' % time_column)

        delta = None
        if index is not None:
            start_time = row[index]
            if time_to_compare is None:
                fmt = '%Y-%m-%d %H:%M:%S'
                time_to_compare = datetime.datetime.now().strftime(fmt)
            delta = date_diff(start_time, time_to_compare)

        tmp_row_list.append(delta)

        return tuple(tmp_row_list)

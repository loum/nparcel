__all__ = [
    "Auditer",
]
import datetime

import nparcel
from nparcel.utils.log import log
from nparcel.utils import date_diff


class Auditer(nparcel.Service):
    """Toll Parcel Portal base Auditer class.

    .. attribute:: bu_id

        dictionary mapping between Business Unit ID (``job.bu_id``
        column) and a human-readable format.  The default is::

            {1: 'Toll Priority',
             2: 'Toll Fast',
             3: 'Toll IPEC'}

    .. attribute:: columns

        list of names of the query columns

    .. attribute::
        *delta_time_column*: raw column name to use for time delta
        (default ``JOB_TS`` which relates to the ``job.job_ts`` column)

    """
    _bu_ids = {}
    _columns = []
    _delta_time_column = 'JOB_TS'

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

    @property
    def columns(self):
        return self._columns

    def set_columns(self, values=None):
        del self._columns[:]
        self._columns = []

        if values is not None:
            log.debug('Setting columns to "%s"' % values)
            self._columns.extend(values)
        else:
            log.debug('Cleared columns list')

    @property
    def delta_time_column(self):
        return self._delta_time_column

    def set_delta_time_column(self, value):
        self._delta_time_column = value
        log.debug('Set delta time column to "%s"' % self.delta_time_column)

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

    def _cleanse(self, header, row):
        """Generic modififications to the raw query result.

        Mods include:
        * prepend ``=`` to the ``CONNOTE_NBR``, ``BARCODE`` and ``ITEM_NBR``
        columns

        **Args:**
            *header*: list of column headers

            *row*: tuple structure that represents the raw row result

        **Returns:**
            the altered *row* tuple structure

        """
        log.debug('Cleansing row "%s"' % str(row))

        tmp_row_list = list(row)

        for i in ['CONNOTE_NBR',
                  'BARCODE',
                  'ITEM_NBR',
                  'JOB_TS',
                  'CREATED_TS',
                  'REFERENCE_NBR',
                  'NOTIFY_TS',
                  'PICKUP_TS']:
            try:
                index = header.index(i)
                log.debug('Prepending "=" to column|value "%s|%s"' %
                          (i, str(tmp_row_list[index])))
                if tmp_row_list[index] is None:
                    tmp_row_list[index] = str()
                else:
                    tmp_row_list[index] = '="%s"' % tmp_row_list[index]
            except ValueError, err:
                pass

        return tuple(tmp_row_list)

    def aged_item(self,
                  headers,
                  row,
                  time_column='CREATED_TS',
                  time_to_compare=None,
                  age=7):
        """Calculate the date delta between the value in the *time_column*
        and *time_to_compare* and compare against *age* (in days).

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

            *age*: the period in days to compare the time delta against

        **Returns:**
            boolean ``True`` if the delta between the dates is
            greater than *age*

            ``False`` otherwise

        """
        is_aged = False

        index = None
        try:
            index = headers.index(time_column)
        except ValueError, err:
            log.warn('No "%s" column in headers' % time_column)

        item_nbr = None
        try:
            item_nbr_index = headers.index('ITEM_NBR')
            item_nbr = row[item_nbr_index]
        except ValueError, err:
            log.warn('No "%s" column in headers' % item_nbr_index)

        delta = None
        if index is not None:
            start_time = row[index]
            if time_to_compare is None:
                fmt = '%Y-%m-%d %H:%M:%S'
                time_to_compare = datetime.datetime.now().strftime(fmt)
            delta = date_diff(start_time, time_to_compare)

        if delta > age:
            is_aged = True

        log.debug('ITEM_NBR "%s" is aged?: %s' % (item_nbr, str(is_aged)))

        return is_aged

    def _cleanse(self, header, row):
        """Generic modififications to the raw query result.

        Mods include:
        * prepend ``=`` to the ``CONNOTE_NBR``, ``BARCODE`` and ``ITEM_NBR``
        columns

        **Args:**
            *header*: list of column headers

            *row*: tuple structure that represents the raw row result

        **Returns:**
            the altered *row* tuple structure

        """
        log.debug('Cleansing row "%s"' % str(row))

        tmp_row_list = list(row)

        for i in ['CONNOTE_NBR',
                  'BARCODE',
                  'ITEM_NBR',
                  'JOB_TS',
                  'CREATED_TS',
                  'REFERENCE_NBR',
                  'NOTIFY_TS',
                  'PICKUP_TS']:
            try:
                index = header.index(i)
                log.debug('Prepending "=" to column|value "%s|%s"' %
                          (i, str(tmp_row_list[index])))
                if tmp_row_list[index] is None:
                    tmp_row_list[index] = str()
                else:
                    tmp_row_list[index] = '="%s"' % tmp_row_list[index]
            except ValueError, err:
                pass

        return tuple(tmp_row_list)

__all__ = [
    "set_scalar",
    "set_date",
    "set_list",
    "set_dict",
]
import inspect
import time
import datetime

from top.utils.log import log


def setter(f, attr_type):
    """Decorator to be used in a context that sets an attribute value.

    There are a few rule that you need to adhere to for this to work
    correctly:

    * The setter decorator name should be the concatenation of ``set_``
    and the attribute name.  For example, if the attribute name is
    ``_my_attr`` then the setter decorator name should be ``set_my_attr``

    .. note:: the assumption here is that you will be setting a *private*
    attribute member.  To adhere to good style guide principles, this
    *private* member should be preceded by a leading underscore ``_``

    Use this decorator if you want to ensure that the attribute is
    assigned *only* a ``scalar`` (i.e. not a list or dictionary) value.

    For example, apply the ``set_scalar`` decorator in the place where you
    define your property setter::

        from top.utils.setter import set_scalar
        ...
        @property
        def my_scalar(self):
            return self._my_scalar

        @set_scalar
        def set_my_scalar(self, value):
            self._bool_var = value

    """

    def wrapped(self, *args):
        # Test that the value is a scalar.
        value = args[0]
        if attr_type == 'tuple' and value is None:
            value = ()
        elif attr_type == 'list' and value is None:
            value = []
        elif attr_type == 'dict' and value is None:
            value = {}

        type_check = False
        if ((not isinstance(value, (list, dict)) and
             (attr_type == 'scalar' or attr_type == 'date')) or
            (type(value) is datetime.datetime and attr_type == 'date') or
            (isinstance(value, tuple) and attr_type == 'tuple') or
            (isinstance(value, list) and attr_type == 'list') or
            (isinstance(value, dict) and attr_type == 'dict')):
            type_check = True

        if not type_check:
            raise TypeError('"%s" is not a %s' % (str(value), attr_type))
        else:
            method_name = f.__name__
            method_name = method_name.replace('set_', '')

            # Set the attribute.  But check that it exists first.
            attr_val = getattr(self, '_%s' % method_name)

            # Special processing for dates.
            if (attr_type == 'date' and value is not None):
                if type(value) is not datetime.datetime:
                    tmp_t = time.strptime(value, "%Y-%m-%d %H:%M:%S")
                    value = datetime.datetime.fromtimestamp(time.mktime(tmp_t))

            setattr(self, '_%s' % method_name, value)
            if isinstance(value, (int, long, float, complex)):
                log.debug('%s.%s set to %s' %
                          (class_name(), method_name, str(value)))
            else:
                log.debug('%s.%s set to "%s"' %
                          (class_name(), method_name, value))

        return(f(self, *args))

    return wrapped


def set_scalar(f):
    return(setter(f, attr_type='scalar'))


def set_date(f):
    return(setter(f, attr_type='date'))


def set_tuple(f):
    return(setter(f, attr_type='tuple'))


def set_list(f):
    return(setter(f, attr_type='list'))


def set_dict(f):
    return(setter(f, attr_type='dict'))


def class_name():
    stack = inspect.stack()
    return stack[1][0].f_locals['self'].__class__.__name__

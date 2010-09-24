#!/usr/bin/env python
"""
Gearman Client Utils
"""
import errno
import select as select_lib
import time

from gearman.constants import DEFAULT_GEARMAN_PORT

class Stopwatch(object):
    """Timer class that keeps track of time remaining"""
    def __init__(self, time_remaining):
        if time_remaining is not None:
            self.stop_time = time.time() + time_remaining
        else:
            self.stop_time = None

    def get_time_remaining(self):
        if self.stop_time is None:
            return None

        current_time = time.time()
        if not self.has_time_remaining(current_time):
            return 0.0

        time_remaining = self.stop_time - current_time
        return time_remaining

    def has_time_remaining(self, time_comparison=None):
        time_comparison = time_comparison or self.get_time_remaining()
        if self.stop_time is None:
            return True

        return bool(time_comparison < self.stop_time)

def disambiguate_server_parameter(hostport_tuple):
    """Takes either a tuple of (address, port) or a string of 'address:port' and disambiguates them for us"""
    if type(hostport_tuple) is tuple:
        gearman_host, gearman_port = hostport_tuple
    elif ':' in hostport_tuple:
        gearman_host, gearman_possible_port = hostport_tuple.split(':')
        gearman_port = int(gearman_possible_port)
    else:
        gearman_host = hostport_tuple
        gearman_port = DEFAULT_GEARMAN_PORT

    return gearman_host, gearman_port

def select(rlist, wlist, xlist, timeout=None):
    """Behave similar to select.select, except ignoring certain types of exceptions"""
    rd_list = []
    wr_list = []
    ex_list = []

    select_args = [rlist, wlist, xlist]
    if timeout is not None:
        select_args.append(timeout)

    try:
        rd_list, wr_list, ex_list = select_lib.select(*select_args)
    except select_lib.error, exc:
        # Ignore interrupted system call, reraise anything else
        if exc[0] != errno.EINTR:
            raise

    return rd_list, wr_list, ex_list

def unlist(given_list):
    """Convert the (possibly) single item list into a single item"""
    list_size = len(given_list)
    if list_size == 0:
        return None
    elif list_size == 1:
        return given_list[0]
    else:
        raise ValueError(list_size)


def any(iterable):
    """Return True if any element of the iterable is true. If the iterable is empty, return False"""
    for element in iterable:
        if element:
            return True
    return False


def all(iterable):
    """Return True if all elements of the iterable are true (or if the iterable is empty)"""
    for element in iterable:
        if not element:
            return False
    return True


class defaultdict(dict):
    """A pure-Python version of Python 2.5's defaultdict
    taken from http://code.activestate.com/recipes/523034-emulate-collectionsdefaultdict/"""
    def __init__(self, default_factory=None, * a, ** kw):
        if (default_factory is not None and
            not hasattr(default_factory, '__call__')):
            raise TypeError('first argument must be callable')
        dict.__init__(self, * a, ** kw)
        self.default_factory = default_factory
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value
    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()
    def copy(self):
        return self.__copy__()
    def __copy__(self):
        return type(self)(self.default_factory, self)
    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))
    def __repr__(self):
        return 'defaultdict(%s, %s)' % (self.default_factory,
                                        dict.__repr__(self))

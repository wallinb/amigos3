import os
import re
import shutil
import tarfile
from collections import MutableMapping
from contextlib import closing
from datetime import datetime
from logging import getLogger
from netrc import netrc
from time import mktime, sleep, time

from honcho.config import (ARCHIVE_DIR, DATA_DIR, DATA_TAGS, LOG_DIR, NETRC_FILEPATH,
                           SBD_QUEUE_DIR, UPLOAD_QUEUE_DIR)

logger = getLogger(__name__)


def ensure_dirs(directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def ensure_all_dirs():
    ensure_dirs(
        [DATA_DIR(tag) for tag in DATA_TAGS]
        + [SBD_QUEUE_DIR, LOG_DIR, UPLOAD_QUEUE_DIR, ARCHIVE_DIR]
    )


def serial_request(serial, command, expected_regex=".+", timeout=10, poll=1):
    if not command.endswith("\r\n"):
        command += "\r\n"

    logger.debug("Sending command to {0}: {1}".format(serial.port, command.strip()))
    serial.flushInput()
    sleep(1)
    serial.write(command)
    sleep(1)
    start_time = time()
    response = ""
    response_length = len(response)
    while time() - start_time < timeout:
        response += serial.read(serial.inWaiting())
        if re.search(expected_regex, response, flags=re.DOTALL):
            break

        new_response_length = len(response)
        if new_response_length > response_length:
            start_time = time()
            response_length = new_response_length

        sleep(poll)
    else:
        logger.debug(
            "Response collected from serial at timeout: {0}".format(response.strip())
        )
        raise Exception("Timed out waiting for expected serial response")

    logger.debug("Response collected from serial: {0}".format(response))

    return response


class OrderedDict(dict, MutableMapping):

    # Methods with direct access to underlying attributes

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError("expected at 1 argument, got %d", len(args))
        if not hasattr(self, "_keys"):
            self._keys = []
        self.update(*args, **kwds)

    def clear(self):
        del self._keys[:]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            self._keys.append(key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __iter__(self):
        return iter(self._keys)

    def __reversed__(self):
        return reversed(self._keys)

    def popitem(self):
        if not self:
            raise KeyError
        key = self._keys.pop()
        value = dict.pop(self, key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        inst_dict = vars(self).copy()
        inst_dict.pop("_keys", None)
        return (self.__class__, (items,), inst_dict)

    # Methods with indirect access via the above methods

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items

    def __repr__(self):
        pairs = ", ".join(map("%r: %r".__mod__, self.items()))
        return "%s({%s})" % (self.__class__.__name__, pairs)

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d


def total_seconds(td):
    return td.days * 24 * 3600 + td.seconds


def format_timedelta(td):
    s = total_seconds(td)
    labels = ("hrs", "min", "sec")
    n = len(labels)
    for i, label in enumerate(labels):
        factor = float(60 ** (n - i - 1))
        count = s / factor
        if count >= 1:
            return "{0:.2f} {1}".format(count, label)


def get_creds(host):
    nrc = netrc(NETRC_FILEPATH)
    user, _, passwd = nrc.hosts[host]

    return user, passwd


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ["bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def make_tarfile(output_filename, filepaths):
    with closing(tarfile.open(output_filename, "w:gz")) as tar:
        for filepath in filepaths:
            tar.add(filepath, arcname=os.path.basename(filepath))


def clear_directory(directory):
    for name in os.listdir(directory):
        path = os.path.join(directory, name)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def average_datetimes(datetimes):
    averaged = datetime.fromtimestamp(
        sum(mktime(dt.timetuple()) for dt in datetimes) / len(datetimes)
    )

    return averaged

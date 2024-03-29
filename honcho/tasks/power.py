import logging
from collections import namedtuple
from datetime import datetime

import honcho.core.data as data
from honcho.config import (DATA_TAGS, IGNORE_LOW_VOLTAGE, MAX_SYSTEM_SLEEP,
                           MIN_SYSTEM_VOLTAGE, TIMESTAMP_FMT)
from honcho.core.onboard import get_voltage
from honcho.core.system import system_standby
from honcho.tasks.common import task

logger = logging.getLogger(__name__)


_DATA_KEYS = ("timestamp", "voltage")
DATA_KEYS = namedtuple("DATA_KEYS", (el.upper() for el in _DATA_KEYS))(*_DATA_KEYS)
PowerSample = namedtuple("PowerSample", DATA_KEYS)
CONVERSION_TO_STRING = {
    DATA_KEYS.TIMESTAMP: "{0:" + TIMESTAMP_FMT + "}",
    DATA_KEYS.VOLTAGE: "{0:.4f}",
}


def voltage_check():
    sample = PowerSample(timestamp=datetime.now(), voltage=get_voltage())
    logger.debug("Current voltage {0:.2f}".format(sample.voltage))
    serialized = data.serialize(sample, CONVERSION_TO_STRING)
    data.log_serialized(serialized, DATA_TAGS.PWR)
    voltage_ok = (sample.voltage >= MIN_SYSTEM_VOLTAGE) or IGNORE_LOW_VOLTAGE
    if not voltage_ok:
        logger.warning(
            "System voltage {0} supply below minimum {1}".format(
                sample.voltage, MIN_SYSTEM_VOLTAGE
            )
        )
        system_standby(MAX_SYSTEM_SLEEP)

    return voltage_ok


@task
def execute():
    voltage_check()

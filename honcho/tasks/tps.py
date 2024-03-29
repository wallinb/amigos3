import logging
import os
from contextlib import closing
from datetime import datetime, timedelta
from time import sleep

from serial import Serial

from honcho.config import (DATA_DIR, DATA_TAGS, GPIO, GPS_BAUD, GPS_PORT,
                           GPS_STARTUP_WAIT, MEASUREMENTS, SECONDS_PER_MEASUREMENT,
                           TIMESTAMP_FILENAME_FMT)
from honcho.core.gpio import powered
from honcho.tasks.archive import archive_filepaths
from honcho.tasks.common import task
from honcho.tasks.upload import queue_filepaths
from honcho.util import clear_directory

logger = logging.getLogger(__name__)


def query_tps(serial, output_filepath):
    start_sequence = [
        "set,/par/ant/rcv/inp,ext\r\n",
        "dm\r\n",
        "dm,,/msg/jps/D1\r\n",
        "dm,,/msg/jps/D2\r\n",
        "set,lock/glo/fcn,n\r\n",
        "em,,def:{0:.2f}&&em,,jps/ET:{0:.2f}\r\n".format(SECONDS_PER_MEASUREMENT),
    ]
    start_command = "em,,def:{0:.2f}&&em,,jps/ET:{0:.2f}\r\n".format(
        SECONDS_PER_MEASUREMENT
    )

    stop_command = "dm"

    logger.debug("Sending TPS setup command sequence")
    for cmd in start_sequence:
        sleep(2)
        serial.write(cmd)

    logger.debug("Starting TPS stream")
    serial.write(start_command)
    end_time = datetime.now() + MEASUREMENTS * timedelta(
        seconds=SECONDS_PER_MEASUREMENT
    )
    with open(output_filepath, "wb") as f:
        data = ""
        while datetime.now() < end_time or data:
            sleep(5)
            data = serial.read(serial.inWaiting())
            logger.debug("Read {0} bytes from tps stream".format(len(data)))
            f.write(data)

    logger.debug("Stopping TPS stream")
    serial.write(stop_command)
    sleep(2)


def get_tps():
    filename = datetime.now().strftime(TIMESTAMP_FILENAME_FMT) + ".tps"
    output_filepath = os.path.join(DATA_DIR(DATA_TAGS.TPS), filename)
    with powered([GPIO.SER, GPIO.GPS]):
        sleep(GPS_STARTUP_WAIT)
        with closing(Serial(GPS_PORT, GPS_BAUD, timeout=60)) as serial:
            query_tps(serial, output_filepath)

    return output_filepath


@task
def execute():
    filepath = get_tps()
    tag = DATA_TAGS.TPS
    queue_filepaths([filepath], postfix=tag)
    archive_filepaths([filepath], postfix=tag)
    clear_directory(DATA_DIR(tag))

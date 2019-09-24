import logging
import os
import shutil
from bisect import bisect
from time import sleep

import amigos.logs as logs
from amigos.util import ensure_dirs

DTS_PULL_DELAY = 60 * 5
DTS_WIN_DATA_DIR = 'Desktop/dts_data'
DTS_RAW_DATA_DIR = "/media/mmcblk0p1/dts_data"
DTS_PROCESSED_DATA_DIR = "/media/mmcblk0p1/dts"
FULL_RESOLUTION_RANGES = [(1000, 1200), (2000, 2200)]

logger = logging.getLogger(__name__)


def ns(tag):
    return "{http://www.witsml.org/schemas/1series}" + tag


def output_filepath(filepath):
    filename = os.path.basename(filepath)
    stem = os.path.splitext(filename)[0]
    return os.path.join(DTS_PROCESSED_DATA_DIR, stem.replace(' ', '_') + '.csv')


def parse_xml(filename):
    import xml.etree.ElementTree as ET

    tree = ET.parse(filename)
    root = tree.getroot()

    log = root.find(ns('log'))
    start_datetime = log.find(ns('startDateTimeIndex')).text
    end_datetime = log.find(ns('endDateTimeIndex')).text

    custom_data = log.find(ns('customData'))
    acquisition_time = custom_data.find(ns('acquisitionTime')).text
    reference_temp = custom_data.find(ns('referenceTemperature')).text
    probe1_temp = custom_data.find(ns('probe1Temperature')).text
    probe2_temp = custom_data.find(ns('probe2Temperature')).text

    measurements = []
    logdata = log.find(ns('logData'))
    for entry in logdata.findall(ns('data')):
        values = [float(el) for el in entry.text.strip().split(",")]
        measurements.append(values)

    return (
        {
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'acquisition_time': acquisition_time,
            'reference_temp': reference_temp,
            'probe1_temp': probe1_temp,
            'probe2_temp': probe2_temp,
        },
        measurements,
    )


def downsample(measurements, factor=4):
    downsampled = []
    for i in range(0, len(measurements), factor):
        means = [
            sum(values) / factor
            for values in zip(*measurements[i : (i + factor)])  # noqa
        ]
        downsampled.append(means)

    return downsampled


def process_measurements(measurements):
    lengths = [el[0] for el in measurements]
    processed = []
    prev_index = 0
    for lower, upper in FULL_RESOLUTION_RANGES:
        i_lower = bisect(lengths, lower)
        # TODO: assert ranges are in increasing order and non-overlapping
        i_upper = bisect(lengths, upper)
        processed.extend(downsample(measurements[prev_index:i_lower]))
        processed.extend(measurements[i_lower:i_upper])
        prev_index = i_upper
    processed.extend(downsample(measurements[prev_index:]))

    return processed


def write(metadata, measurements, filepath):
    with open(filepath, "w") as f:
        for k, v in metadata.iteritems():
            f.write('# ' + str(k) + '=' + str(v) + '\n')

        f.write("length,stokes,anti_stokes,reverse_stokes,reverse_anti_stokes,temp\n")
        for row in measurements:
            f.write(','.join([str(el) for el in row]) + '\n')


def acquire():
    """Entry point of DTS files retrival and execution plus time update on windows unit
    """
    from gpio import dts_on, dts_off, hub_on, hub_off
    from ssh import SSH

    logger.info("Turning on DTS and windows unit")
    hub_on(1)
    # win_on()
    dts_on(1)

    logger.info("Sleeping {0} seconds for acquisition".format(DTS_PULL_DELAY))
    sleep(DTS_PULL_DELAY)

    logger.info("Pulling files from windows unit")
    ssh = SSH("admin", "192.168.0.50")
    win_data_glob = os.path.join(DTS_WIN_DATA_DIR, "*")

    ensure_dirs([DTS_RAW_DATA_DIR, DTS_PROCESSED_DATA_DIR])

    ssh.copy(win_data_glob, DTS_RAW_DATA_DIR, recursive=True)

    filepaths = []
    for root, _, filenames in os.walk(DTS_RAW_DATA_DIR):
        filepaths.extend(
            [
                os.path.join(root, filename)
                for filename in filenames
                if filename.endswith('xml')
            ]
        )
    logger.info("Found {0} dts files".format(len(filepaths)))

    for filepath in filepaths:
        logger.info("Processing {0}".format(filepath))
        metadata, measurements = parse_xml(filepath)
        measurements = process_measurements(measurements)
        write(metadata, measurements, output_filepath(filepath))
        break

    logger.info("Processing DTS complete, cleaning up")
    ssh.execute("rm -rf {glob}".format(glob=win_data_glob))
    shutil.rmtree(DTS_RAW_DATA_DIR)

    hub_off(1)
    dts_off(1)
    # win_off()


if __name__ == "__main__":
    logs.init_logging(logging.DEBUG)
    acquire()
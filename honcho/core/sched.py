import logging
from datetime import datetime
from time import sleep

from honcho.config import (MAX_SYSTEM_SLEEP, MODE, MODES, SCHEDULE_IDLE_CHECK_INTERVAL,
                           SCHEDULE_NAMES, SCHEDULE_START_TIMES, SCHEDULES)
from honcho.core.gpio import set_awake_gpio_state
from honcho.core.system import get_ps, system_standby
from honcho.logs import init_logging
from honcho.tasks import import_task
from honcho.tasks.power import voltage_check
from honcho.util import ensure_all_dirs
from schedule.schedule import Scheduler

logger = logging.getLogger(__name__)


def select_schedule(date):
    if MODE in (MODES.SAFE, MODES.TEST, MODES.SUMMER, MODES.WINTER):
        return MODE
    elif MODE == MODES.NORMAL:
        winter_start = datetime(
            year=date.year,
            month=SCHEDULE_START_TIMES[SCHEDULE_NAMES.WINTER]["month"],
            day=SCHEDULE_START_TIMES[SCHEDULE_NAMES.WINTER]["day"],
        )
        summer_start = datetime(
            year=date.year,
            month=SCHEDULE_START_TIMES[SCHEDULE_NAMES.SUMMER]["month"],
            day=SCHEDULE_START_TIMES[SCHEDULE_NAMES.SUMMER]["day"],
        )
        if (date >= winter_start) and (date < summer_start):
            return SCHEDULE_NAMES.WINTER
        else:
            return SCHEDULE_NAMES.SUMMER
    else:
        raise Exception("Unexpected MODE: {0}".format(MODE))


def load_schedule(scheduler, config):
    for spec, task_module in config:
        task = import_task(task_module)
        task.execute.__name__ = task_module
        try:
            eval(spec).do(task.execute)
        except (SyntaxError, NameError):
            continue


def idle_check(scheduler):
    idle_minutes = scheduler.idle_seconds / 60.0
    if idle_minutes > 2:
        logger.info("Schedule idle for {0:.0f} minutes".format(idle_minutes))
        system_standby(min(int(idle_minutes - 1), MAX_SYSTEM_SLEEP))


def print_summary():
    name = select_schedule(datetime.now())
    print("Schedule: {0}".format(name))

    scheduler = Scheduler()
    load_schedule(scheduler, SCHEDULES[name])
    for job in scheduler.jobs:
        print(job)


def get_schedule_processes():
    ps = get_ps()
    schedule_processes = [process for process in ps if "schedule" in process.command]
    return schedule_processes


def execute():
    ensure_all_dirs()
    init_logging()
    set_awake_gpio_state()

    name = select_schedule(datetime.now())
    logger.info("Running schedule: {0}".format(name))
    scheduler = Scheduler()

    load_schedule(scheduler, SCHEDULES[name])

    while True:
        sleep(SCHEDULE_IDLE_CHECK_INTERVAL)
        if not voltage_check():
            continue

        scheduler.run_pending()
        idle_check(scheduler)


if __name__ == "__main__":
    execute()

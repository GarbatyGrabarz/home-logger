#!/usr/bin/python3

import time
import logging
import os
from loglibs.sensors import Sensors
from loglibs.ifdb import IFDB
from loglibs.config import TEMP_OFFSET, GAS_BASE, HUM_BASE


def Main_program():
    sensors = Sensors(TEMP_OFFSET, GAS_BASE, HUM_BASE)
    db = os.popen('hostname').readline().replace('\n', '')
    database = IFDB('env_logs', 'grafana', 'raspberrypi', db)

    start_time = time.time()
    delay = 60  # In seconds

    while True:

        sensors.read()
        sensors.read_air()

        if time.time() - start_time > delay:

            database.add_points(sensors.data)

            formatted_data = (f'{sensors.data.temp:.1f} \u00b0C'
                              f' | {sensors.data.hum:.1f} %RH'
                              f' | {sensors.data.pres:.0f} hPa')

            if sensors.data.air is not None:
                formatted_data += f' | Air quality: {sensors.data.air:.0f}%'

            print(formatted_data)
            start_time = time.time()

        time.sleep(1)


if __name__ == "__main__":

    logging.basicConfig(filename='/home/pi/logger.log',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    try:
        Main_program()

    except Exception as e:
        logging.critical("%s", e)
        raise Exception(f'Program crashed: {e}')

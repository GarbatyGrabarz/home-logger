#!/usr/bin/python3

import time
import logging
from loglibs.sensors import Sensors
from loglibs.ifdb import IFDB
from loglibs.config import TEMP_OFFSET
from loglibs.config import DATABASE


def Main_program():
    sensors = Sensors(TEMP_OFFSET)
    database = IFDB('env_logs', 'grafana', 'raspberrypi', DATABASE)

    while True:

        sensors.read()
        database.add_points(sensors.data)

        data_to_display = (f'{sensors.data.temp:.1f} \u00b0C '
                           f'{sensors.data.hum:.1f}% '
                           f'{sensors.data.pres:.0f} hPa ')

        print(data_to_display)
        time.sleep(60)


if __name__ == "__main__":

    logging.basicConfig(filename='/home/pi/Logger_logs.log',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    try:
        Main_program()

    except Exception as e:
        logging.critical("%s", e)

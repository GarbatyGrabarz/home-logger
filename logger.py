#!/usr/bin/python3

import time
import logging
from loglibs.sensors import Sensors
from loglibs.ifdb import IFDB
from loglibs.config import TEMP_OFFSET, GAS_BASE, HUM_BASE


def Main_program():
    sensors = Sensors(TEMP_OFFSET, GAS_BASE)
    db = os.popen('hostname').readline().replace('\n', '')
    database = IFDB('env_logs', 'grafana', 'raspberrypi', db)

    while True:

        sensors.data = sensors.data_structure()  # Reset all values to default
        sensors.read()
        formatted_data = (f'{sensors.data.temp:.1f} \u00b0C'
                          f' | {sensors.data.hum:.1f} %RH'
                          f' | {sensors.data.pres:.0f} hPa')

        if sensors.air_readout():
            formatted_data += f' | Air quality: {sensors.data.air:.0f}%'

        database.add_points(sensors.data)
        print(formatted_data)
        time.sleep(60)


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

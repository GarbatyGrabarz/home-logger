#!/usr/bin/python3

import time
import logging
import configparser

from loglibs.config_control import valid_config
from loglibs.sensors import Sensors
from loglibs.ifdb import IFDB


def Main_program():
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not valid_config(config):
        raise SystemExit('Config.ini is invalid')

    sensors = Sensors(config)
    database = IFDB(config)
    start_time = time.time()
    delay = float(config['Logger']['DELAY'])

    while True:

        sensors.read()
        sensors.read_air()

        if time.time() - start_time > delay:

            database.add_points(sensors.UCT_timestamp, sensors.data)

            temp = sensors.data.get('Temperature')
            hum = sensors.data.get('Humidity')
            press = sensors.data.get('Pressure')
            air = sensors.data.get('Air_quality')

            output = f'{temp:.1f} \u00b0C | {hum:.1f} %RH | {press:.0f} hPa'
            if air is not None:
                output += f' | Air quality: {air:.0f}%'

            print(output)
            start_time = time.time()

        time.sleep(1)


if __name__ == "__main__":

    logging.basicConfig(
        filename='loglibs/logger.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    try:
        Main_program()

    except Exception as e:
        logging.critical("%s", e)
        raise Exception(f'Program crashed: {e}')

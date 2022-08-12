#!/usr/bin/python3

import time
import logging
import configparser

from loglibs.config_control import valid_config, CheckFlag
from loglibs.sensors import Sensors
from loglibs.ifdb import IFDB


def Main_program():
    # Loading config
    config = configparser.ConfigParser()
    config.read('loglibs/config.ini')

    # Checking config
    if not valid_config(config):
        error_msg = 'Config.ini is invalid'
        print(error_msg)  # Exception was not shown in the terminal
        raise SystemExit(error_msg)

    # Creating objects and variables
    sensors = Sensors(config)
    database = IFDB(config)
    start_time = time.time()
    delay = float(config['Logger']['DELAY'])

    while True:

        sensors.read()
        if CheckFlag(config['Air quality']['GET_AIR']):
            sensors.read_air()

        if time.time() - start_time > delay:

            if database.add_points(sensors.UCT_timestamp, sensors.data):

                temp = sensors.data.get('Temperature')
                hum = sensors.data.get('Humidity')
                press = sensors.data.get('Pressure')
                air = sensors.data.get('Air_quality')

                out = f'{temp:.1f} \u00b0C | {hum:.1f} %RH | {press:.0f} hPa'
                if air is not None:
                    out += f' | Air quality: {air:.0f}%'

                print(out)
            else:
                print(f'Problem with connection to {database.host}')
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

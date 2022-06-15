import bme680
import time
import configparser
from datetime import datetime


try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except (RuntimeError, IOError):
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

bt = input('How long to burn the sensor (default: 20 min)?\n')
try:
    bt = float(bt)
except ValueError:
    bt = 20

# start_time and curr_time ensure that the
# burn_in_time (in seconds) is kept track of.
start_time = time.time()
curr_time = time.time()
burn_in_data = []
burn_in_time = bt * 60

# Collect gas resistance burn-in values, then use the average
# of the last 50 values to set the upper limit for calculating
# gas_baseline.
timestamp = datetime.now().strftime('%Y.%m.%d %H:%M')

print(f'{timestamp} Collecting gas resistance data for {bt:.0f} mins\n')
while curr_time - start_time < burn_in_time:
    curr_time = time.time()
    if sensor.get_sensor_data() and sensor.data.heat_stable:
        gas = sensor.data.gas_resistance
        burn_in_data.append(gas)
        print(f'\rGas: {gas:.0f} \u03A9', end='\r')
        time.sleep(1)

gas_baseline = sum(burn_in_data[-50:]) / 50.0
gas_max = max(burn_in_data)
timestamp = datetime.now().strftime('%Y.%m.%d %H:%M')

print(f'\n Gas baseline = {gas_baseline:.0f} \u03A9')
with open('gas_resistance_baseline.txt', 'a') as file:
    file.write(f'{timestamp} - '
               f'Average: {gas_baseline:.0f}, '
               f'Max: {gas_max:.0f}, '
               f'Burn time: {bt:.0f} min\n')

config = configparser.ConfigParser()
config.read('config.ini')
config['Air quality'] = {'GAS_BASE': gas_baseline}
with open('config.ini', 'w') as configfile:
    config.write(configfile)

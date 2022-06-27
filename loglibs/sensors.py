import os
import pytz
from datetime import datetime
import bme680
from config_control import CheckFlag


class Sensors(object):
    """Class wrapper for handling all sensors in one place"""

    def __init__(self, configparser_obj):
        temp_config = configparser_obj['Temperature']
        air_config = configparser_obj['Air quality']
        db_config = configparser_obj['Database']

        self.timezone = pytz.timezone(db_config['TIMEZONE'])
        self.offset = float(temp_config['TEMP_OFFSET'])
        self.get_air = CheckFlag(air_config['GET_AIR'])
        self.gas_base = float(air_config['GAS_BASE'])
        self.hum_base = float(air_config['HUM_BASE'])
        self.hum_weight = float(air_config['HUM_CONTRIBUTION']) / 100
        self.gas_weight = 1 - self.hum_weight

        self.bme = bme680.BME680()
        self._setup_sensors()
        self.data = dict()
        self.UCT_timestamp = None

    def _setup_sensors(self):
        """This method is to set all parameters for sensors in one place"""

        """The higher the oversampling, the greater the reduction in noise,
        but also reduction of accuracy.
        Available: OS_NONE, OS_1X, OS_2X, OS_4X, OS_8X, OS_16X"""
        self.bme.set_humidity_oversample(bme680.OS_2X)
        self.bme.set_pressure_oversample(bme680.OS_2X)  # Was OS_4X
        self.bme.set_temperature_oversample(bme680.OS_2X)  # Was OS_8X

        if self.get_air:
            self.bme.set_gas_status(bme680.ENABLE_GAS_MEAS)
            self.bme.set_gas_heater_temperature(320)
            self.bme.set_gas_heater_duration(150)
            self.bme.select_gas_heater_profile(0)
        else:
            self.bme.set_gas_status(bme680.DISABLE_GAS_MEAS)


        """Set tepmerature offet"""
        self.bme.set_temp_offset(self.offset)

    def _get_cpu_temp(self):
        """Reading Raspberry PI CPU temp and returns as float
        (converted from string) If string stripping fails it returns float 0"""
        t_read = os.popen("vcgencmd measure_temp").readline()
        try:
            cpu_temp = float(t_read.replace("temp=", "").replace("'C\n", ""))
        except ValueError:
            cpu_temp = float(0)
        return cpu_temp

    def _to_uct(self, time):
        """The database uses UCT timezone so all date-time has to be
        converted to UCT-equivalent, e.g. 15:00 in Sweden
        is reported as 13:00 UCT"""
        UCT_Time = self.timezone.localize(time, is_dst=True)
        UCT_Time = UCT_Time.astimezone(pytz.utc)
        return UCT_Time

    def _to_absHum(self, temp, rel_hum, version='wiki'):
        """Calculates absolute humidity [g/m3] from relative humidity
        using Tetens equation: https://en.wikipedia.org/wiki/Tetens_equation

        temp - Temperature [°C]
        rel_hum - Relative humidity [%] (meaning values 0 - 100)

        There is a difference in constants found here:
        https://www.youtube.com/watch?v=EXjbjIgTgsA
        The video is published at a later date. It could mean some update or
        refinement of constants. The difference is on 3rd decimal place"""
        import math

        Mw = 18.02   # Constant: Molecular weigth of water [g/mol]
        R = 8.31  # Constant: Universal gas constant [J/mol*K]
        K = temp + 273.15  # Temperature [K]

        constants = {
            'wiki': {
                'b': 17.27,
                'c': 237.3},
            'youtube': {
                'b': 17.502,
                'c': 240.97}}

        b = constants[version]['b']
        c = constants[version]['c']

        saturation_vapor_pressure = 0.61078 * math.exp(
            b * temp / (temp + c))  # [kPa]
        vapor_pressure = rel_hum / 100 * saturation_vapor_pressure  # [kPa]
        vapor_density = (vapor_pressure * Mw) / (R * K) * 1000  # [g/m3]

        return vapor_density

    def read(self):
        while not self.bme.get_sensor_data():
            pass  # Wait for the sensor

        self.UCT_timestamp = self._to_uct(datetime.now())
        self.data['CPU'] = self._get_cpu_temp()
        self.data['Temperature'] = self.bme.data.temperature
        self.data['Pressure'] = self.bme.data.pressure
        self.data['Humidity'] = self.bme.data.humidity
        self.data['Absolute humidity'] = self._to_absHum(
            self.bme.data.temperature,
            self.bme.data.humidity)

    def read_air(self):
        if self.bme.get_sensor_data() and self.bme.data.heat_stable:
            gas = self.bme.data.gas_resistance

            gas_offset = self.gas_base - gas
            hum_offset = self.data['Humidity'] - self.hum_base
            self.data['Gas resistance'] = gas

            # Calculate hum_score as the distance from the hum_base
            if hum_offset > 0:
                hum_score = 100 - self.hum_base - hum_offset
                hum_score /= 100 - self.hum_base
                hum_score *= self.hum_weight

            else:
                hum_score = self.hum_base + hum_offset
                hum_score /= self.hum_base
                hum_score *= self.hum_weight

            # Calculate gas_score as the distance from the gas_base
            if gas_offset > 0:
                gas_score = gas / self.gas_base
                gas_score *= self.gas_weight

            else:
                gas_score = self.gas_weight

            # Calculate air_quality_score.
            self.data['Air quality'] = (hum_score + gas_score) * 100

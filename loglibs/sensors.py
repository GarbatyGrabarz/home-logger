import os
from datetime import datetime
import bme680


class Sensors(object):
    """Class wrapper for handling all sensors in one place"""

    def __init__(self, TEMP_OFFSET, GAS_BASE):
        self.offset = TEMP_OFFSET

        self.gas_base = GAS_BASE
        self.hum_base = 40.0

        self.hum_weight = 0.25
        self.gas_weight = 1 - self.hum_weight

        self.bme = bme680.BME680()
        self._setup_sensors()

    class data_structure(object):
        def __init__(self):
            """Default values are delibretly incorrect"""
            self.timestamp = datetime.strptime('2000-01-01', '%Y-%m-%d')
            self.cpu = float(0)
            self.temp = float(0)
            self.pres = float(0)
            self.hum = float(-10)
            self.air = float(-1)

    def _setup_sensors(self):
        """This method is to set all parameters for sensors in one place"""

        """The higher the oversampling, the greater the reduction in noise,
        but also reduction of accuracy.
        Available: OS_NONE, OS_1X, OS_2X, OS_4X, OS_8X, OS_16X"""
        self.bme.set_humidity_oversample(bme680.OS_2X)
        self.bme.set_pressure_oversample(bme680.OS_2X)  # Was OS_4X
        self.bme.set_temperature_oversample(bme680.OS_2X)  # Was OS_8X

        self.bme.set_gas_status(bme680.ENABLE_GAS_MEAS)
        self.bme.set_gas_heater_temperature(320)
        self.bme.set_gas_heater_duration(150)
        self.bme.select_gas_heater_profile(0)

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

    def read(self):
        """Gets data from all sensors"""
        self.data = self.data_structure()  # Reset all values to default

        while not self.bme.get_sensor_data():
            pass

        self.data.cpu = self._get_cpu_temp()
        self.data.timestamp = datetime.now()

        if self.bme.get_sensor_data():
            self.data.temp = self.bme.data.temperature
            self.data.pres = self.bme.data.pressure
            self.data.hum = self.bme.data.humidity

        if self.bme.get_sensor_data() and self.bme.data.heat_stable:
            gas = self.bme.data.gas_resistance

            gas_offset = self.gas_base - gas
            hum_offset = self.data.hum - self.hum_base

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
            self.data.air = (hum_score + gas_score) * 100

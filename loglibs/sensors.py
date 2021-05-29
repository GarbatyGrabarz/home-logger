import os
from datetime import datetime
import bme680


class Sensors(object):
    """Class wrapper for handling all sensors in one place"""

    def __init__(self, TEMP_OFFSET):
        self.bme = bme680.BME680()
        self._setup_sensors()
        self.data = self.data_structure()
        self.offset = TEMP_OFFSET

    class data_structure(object):
        def __init__(self):
            """Default values are delibretly incorrect"""
            self.timestamp = datetime.strptime('2000-01-01', '%Y-%m-%d')
            self.cpu = float(0)
            self.temp = float(0)
            self.pres = float(0)
            self.hum = float(-10)

    def _setup_sensors(self):
        """This method is to set all parameters for sensors in one place"""

        """The higher the oversampling, the greater the reduction in noise,
        but also reduction of accuracy.
        Available: OS_NONE, OS_1X, OS_2X, OS_4X, OS_8X, OS_16X"""
        self.bme.set_humidity_oversample(bme680.OS_2X)
        self.bme.set_pressure_oversample(bme680.OS_2X)  # Was OS_4X
        self.bme.set_temperature_oversample(bme680.OS_2X)  # Was OS_8X

        """Turn off measurements of Air quality. It warms up plate inside
        the sensor potentially affecting the temp readings and its
        sensitivity will not satisfy our needs anyway """
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

    def read(self):
        """Gets data from all sensors"""
        self.data.cpu = self._get_cpu_temp()
        self.data.timestamp = datetime.now()
        if self.bme.get_sensor_data():
            self.data.temp = self.bme.data.temperature
            self.data.pres = self.bme.data.pressure
            self.data.hum = self.bme.data.humidity

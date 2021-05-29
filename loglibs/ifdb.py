import pytz
from influxdb import InfluxDBClient


class IFDB(object):
    """This is a wrapper class for uploading data points to InfluxDB"""

    def __init__(self, measurement, username, password, database):
        self.timezone = pytz.timezone('Europe/Stockholm')
        self.measurement = measurement
        self.username = username
        self.password = password
        self.database = database

    def add_points(self, data):
        self._connect()
        self._format_and_write(data)
        self.client.close()

    def _connect(self):
        self.client = InfluxDBClient(host="localhost",
                                     port=8086,
                                     username=self.username,
                                     password=self.password,
                                     database=self.database
                                     )

    def _format_and_write(self, data):
        """Formatting data for the upload. Uses "data" which is subclass
        of sensors class defined in main logger script"""
        body = [
                    {
                        "measurement": self.measurement,
                        "time": self._to_uct(data.timestamp),
                        "fields": {
                            "CPU": data.cpu,
                            "Temperature": data.temp,
                            "Pressure": data.pres,
                            "Humidity": data.hum
                        }
                    }
                ]

        self.client.write_points(body)

    def _to_uct(self, time):
        """The database uses UCT timezone so all date-time has to be
        converted to UCT-equivalent, e.g. 15:00 in Sweden
        is reported as 13:00 UCT"""
        UCT_Time = self.timezone.localize(time, is_dst=True)
        UCT_Time = UCT_Time.astimezone(pytz.utc)
        return UCT_Time

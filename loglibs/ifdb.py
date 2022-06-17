from influxdb import InfluxDBClient
from requests.exceptions import ConnectTimeout


class IFDB(object):
    """This is a wrapper class for uploading data points to InfluxDB"""

    def __init__(self, configparser_obj):
        config = configparser_obj['Database']
        self.measurement = config['MEASUREMENT']
        self.host = config['HOST']
        self.username = config['USER']
        self.password = config['PASS']
        self.database = config['DATABASE']

    def add_points(self, UCT_timestamp, data_dict):
        try:
            self._connect()
            self._pack_and_write(UCT_timestamp, data_dict)
            self.client.close()
            return True
        except ConnectTimeout:
            return False

    def _connect(self):
        self.client = InfluxDBClient(
            host=self.host,
            port=8086,
            username=self.username,
            password=self.password,
            database=self.database,
            timeout=3
            )

    def _pack_and_write(self, UCT_timestamp, data_dict):
        """Formatting data for the upload. Uses "data" which is subclass
        of sensors class defined in main logger script"""
        body = [{
            "measurement": self.measurement,
            "time": UCT_timestamp,
            "fields": data_dict
            }]
        self.client.write_points(body)

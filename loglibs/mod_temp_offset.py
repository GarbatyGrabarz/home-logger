import configparser

config = configparser.ConfigParser()
config.read('config.ini')
offset = config['Temperature']['TEMP_OFFSET']

offset_correction = input('How much to correct the offset?\n')
try:
    offset_correction = float(offset_correction)
except ValueError:
    offset_correction = 0

config['Temperature']['TEMP_OFFSET'] = offset + offset_correction

with open('config.ini', 'w') as configfile:
    config.write(configfile)

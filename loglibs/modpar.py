#!/usr/bin/env python3

import configparser
from itertools import count
import time


print('Warning! This script does not control for data correctness!!!')

# Load config and prepare variables
config = configparser.ConfigParser()
config.read('config.ini')
position = count(1)
list_of_sections = config.sections()
items = dict()

# Build dictionary
for section in list_of_sections:
    for item in config[section]:
        items[f'{next(position)}'] = {'section': section, 'item': item}

del section, item


def Choice_level1():
    """Handles selection of parameters. Returns valid number in str format"""
    while True:
        print('Which parameter do you want to modify?\n')
        for key in items:
            print(key, items[key]['item'])
        c = input('\nChosen parameter: ')
        if items.get(c) is not None:
            return c
        else:
            print('\nIncorrect. Try again.\n')
            time.sleep(1.5)


def Summary(c):
    """Prints the current value of chosen parameter"""
    global items
    section = items[c]['section']
    item = items[c]['item']
    val = config[section][item]
    print(f"Current value of '{item}' is {val}")


def temperature_offset():
    global config
    offset = config['Temperature']['TEMP_OFFSET']
    correction = input('How much to correct the offset?\n')
    try:
        correction = float(correction)
    except ValueError:
        correction = 0

    config['Temperature']['TEMP_OFFSET'] = str(float(offset) + correction)

    with open('config.ini', 'w') as configfile:
        config.write(configfile)


def mod_parameter(c):
    global config
    section = items[c]['section']
    item = items[c]['item']
    inp = input('New value: ')
    config[section][item] = inp
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


while True:
    c = Choice_level1()
    Summary(c)
    if items[c]['item'] == 'temp_offset':
        while True:
            c3 = input('\nChange or modify the value? [c/m]\n')
            if c3.lower() == 'c':
                mod_parameter(c)
                break
            elif c3.lower() == 'm':
                temperature_offset()
                break
            else:
                continue
    else:
        mod_parameter(c)
    c3 = input('\nDo you want to modify more? [y/n]\n')
    if c3.lower() == 'y':
        pass
    else:
        break

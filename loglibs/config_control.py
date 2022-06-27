import pytz


def valid_config(ini):
    """The function takes configparser object as an input and check for
    corectness. Named ini to make it shorter"""
    try:
        """ First load all variables to see if they exist (KeyError if not)
        No file also renders KeyError"""
        delay = float(ini['Logger']['DELAY'])
        _ = float(ini['Temperature']['TEMP_OFFSET'])
        gas_base = float(ini['Air quality']['GAS_BASE'])
        hum_base = float(ini['Air quality']['HUM_BASE'])
        hum_contribution = float(ini['Air quality']['HUM_CONTRIBUTION'])

        # Strings
        _ = ini['Database']['HOST']
        _ = ini['Database']['USER']
        _ = ini['Database']['PASS']
        _ = ini['Database']['DATABASE']
        _ = ini['Database']['MEASUREMENT']
        tz = ini['Database']['TIMEZONE']

        # Flags
        get_air = CheckFlag(ini['Air quality']['GET_AIR'])
        if get_air is True or get_air is False:
            pass
        else:
            print('Flag is not True or False')
            raise ValueError

        """ Check if data is correct"""

        if delay < 2:
            print('Delay too small')
            raise ValueError

        if gas_base <= 0:
            print('Gas base too small')
            raise ValueError

        if hum_base < 0 or hum_base > 100:
            print('Humidity base outside of 0 - 100 range')
            raise ValueError

        if hum_contribution < 0 or hum_contribution > 100:
            print('Humidity contribution outside of 0 - 100 range')
            raise ValueError

        try:
            _ = pytz.timezone(tz)
        except pytz.UnknownTimeZoneError:
            print('Incorrect time zone')
            raise ValueError

    except KeyError:
        print(
            'Missing variable (or file). See example_config.ini for reference'
            )
        return False

    except ValueError:
        return False

    return True


def CheckFlag(text):
    if text.lower() == 'true':
        return True
    elif text.lower() == 'false':
        return False
    else:
        return None

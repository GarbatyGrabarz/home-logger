# Introduction
This program is used on multiple units of Raspberry Pi (Zero W to be exact) with a BME680 sensor connected to it. I have used the one from [Pimoroni](https://shop.pimoroni.com/products/bme680-breakout?variant=12491552129107) but I am guessing other manufacturers should work too. The purpose of the program is to collect the data from the sensor and send it to InfluxDB database. The data is later visualized with [Grafana](https://grafana.com/). As a bonus it logs the CPU of the Raspberry Pi.

Originally each Raspberry was running it's own database to avoid issues when the LAN is down, but I have realized it is used for recording room temperature and not some fancy experiments so I have changed the config to send the data to a centralized database. In case of connection issues the program will output a message and move on like nothing happened.

Details of how things work are covered more in the config section of this document.

# Requirements

*   Python libraries:
    *   [InfluxDB client](https://pypi.org/project/influxdb/)
    *   [BME680](https://pypi.org/project/bme280/)
    *   [pytz](https://pypi.org/project/pytz/)
    *   [requests](https://pypi.org/project/requests/)
*   Installed and configured InfluxDB (time series database). That means creating a database and a user (with all privileges). Database can be on the computer running this code or on a different one.
*   Remember that files that were to be executed (`logger.py`, `modpar.py`, `baseline.py`) must have execute permission (`sudo chmod +x ...`)

---

# Installation

* Get the code
* Install necessary libraries
* Make a copy of `example_config.ini`and rename it to `config.ini`. That will be your main config (it's included in .gitignore so it should not be overwritten)
* Fill the config with correct information
* Make sure you have a running and configured InfluxDB database
* Run the code

## InfluxDB configuration

I would be too lazy to search the internet for the config information so why should I assume you wouldn't? Here is a cheat sheet :D

Type in the terminal `influx` to start the program. Then type the lines below. Content of { } is of course up to you, you also skip the brackets. For example, the first line could be `create database my_database`

```plaintext
create database {db_name}
create user {user} with password '{password}' with all privileges
grant all privileges on {db_name} to {user}
```

---

# Configuration (config.ini)
Configuration should be filled correctly before the start. However, you might find yourself in need of changing some parameters. One of the way is to edit the file and reboot the program, but I found the in-terminal editor quite clumsy, not to mention I was running 5 loggers at the same time. There are programs that allow you to send the same command to multiple units but it was not working with text editing. I have made a small program (`modpar.py`) that essentially serves as a single-parameter editor that can be operated with those programs sending the same command to multiple units. Note that there is no check for data correctness and the program has to be restarted to take effect.

## Logger

**DELAY** - How many seconds to wait between collecting data point (minimum 2 seconds)

## Database

**HOST** - Address (typically IP) where your InfluxDB is located. If you have the database on the same device `localhost` should work.
**USER** and **PASS** - User and password to access the database.
**DATABASE** - Name you gave the database when you created it.
**MEASUREMENT** - created dynamically so whatever you type here should be OK. Feel free to keep the default name.
**TIMEZONE** - Time zone of the place you are getting the data from. It must work with pytz. If you are not sure you can either check it [here](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568) or run that code yourself:

```python
import pytz
pytz.all_timezones
```

## Temperature
The sensor sometimes gives values that are way off. From what I've gathered from the net, the most likely culprit is simple lack of factory calibration. In either case the default -5 is a good start but I have run the program for a while and was comparing the reported temperature with some thermometers I've bought. All very hand-waving and inaccurate but better than guessing.

## Air quality
Here is the thing... This whole air quality sensing is *very* weird.

### How it works?
How the sensor works is quite simple: it burns the gas and checks what resistance came out of it (suuuuuper simplifying). Clean air - high resistance, "dirty" air - low resistance. So what you do is, you get a **reference** by burning some clean air, and that resistance becomes your 100%. Everything recorded later will be dirtier, thus lower resistance, thus lower percentage. That reference is the **GAS_BASE** in the config.

Let's say I recorded the reference is a clean environment and got 150 kΩ (the sensor uses Ω but let's use fewer zeros for our mental health). After sitting in the room for a while, sweating and breathing out I get 90 kΩ resulting in 60% air quality (150 / 90).

To get the reference value check out the end of this document

### What's up with the humidity?
I have read [somewhere](https://github.com/G6EJD/BME680-Example) that humidity also affects our perception of air quality and that humans prefer 40% relative humidity (**HUM_BASE** in the config). How much each factor (quality or humidity) affects the score is determined by **HUM_CONTRIBUTION** which is expressed in percentage. Example: 25 means that only 1/4 of the humidity score (how far humidity is from the selected base) affects the overall airt quality score.

That text mentions also contribution from the temperature but as we all know from the Thermostat Wars, this parameter seems to be much more individual based so I have ignored it.

### Does it really work?
No. At least I am not convinced. That's why **GET_AIR** flag exists so this feature can be completely switched off.

First, the most obvious problem is getting a reference that is not clean enough and ending up with scores higher than 100% which makes no practical sense (program caps at 100%).

The other problem is getting air that is too clean. This results with your rooms getting at best low scores (No higher than 60% in my case).

Perhaps when you have just one sensor you would be happy with the results. They do make sense. You see quality going up when you open the window, etc. Unfortunately I had 5 sensors. I calibrated them on a terrace on a pleasant evening... every day for 5 days! After that I was running tests by having all 5 loggers closed in one room that nobody was entering for days. The values were all over the place. What resulted with similar values was manually picking the gas resistances. Since I run the calibration so many times I had multiple values to choose from for each sensor. Fo some I chose the highest recorded, for some second highest. But how does it make sense? I take values from calibration from different days, and naturally different conditions. This approach was simply too sloppy for me.

In the future I intend to return to the issue and spend more time on it. Perhaps I will get more luck when I focus on one issue and not the whole system working. [This](https://github.com/rstoermer/bsec_bme680_python) looks very promising.

---

# Getting the reference

Run the `baseline.py`. It should by default run the program for 20 minutes (you can change the time) and keep burning-in the gas. After that it does 3 things:
1. It saves all recorded resistances into `baseline_raw.txt`. This file will be overwritten every time.
2. It calculates the average and maximum of the last 50 values and saves it to `baseline_history.txt`. This file will be appended so you actually have some record of what you are doing.
3. Updates the config file with the average of the last 50 values so you don't have to do it manually
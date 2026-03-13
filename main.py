import asyncio
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import sys
import logging as log
import argparse
import secrets
import time as timer
import re

os.chdir(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))                                # Set working directory to script location

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")                                # -v / --verbose for verbose logging
parser.add_argument("-vvvv", "--debug", action="store_true", help="Debugging mode")                             # -vvvv / --debug for debug logging
parser.add_argument("-s", "--run-once", action="store_true", help="Log data once.")                             # -s / --run-once for single log
parser.add_argument("-a", "--mac-address", help="Use specific MAC-address")                                     # -a / --mac-address for specifying a MAC-address without environment variables (takes precedence over environment variables)
parser.add_argument("-e", "--emulate", action="store_true", help="Generate plausible pseudorandom readings")    # -e / --emulate for generating pseudorandom data that could be plausible readings (takes precedence over flag specified MAC and environment variables)
parser.add_argument("-d", "--delay", help="Specify delay between readings (in milliseconds)")                    # -d / --delay for specifying a time between readings in milliseconds 
args = parser.parse_args()

DB_PATH = Path('data/data.db')                  # Database location
os.environ["RUUVI_BLE_ADAPTER"] = "bleak"       # BLE adapter
rand = secrets.SystemRandom()                   # Random number generator for emulation

# Configure logging once based on args
if args.debug:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)
    log.info("Debug mode enabled.")
elif args.verbose:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)
    log.info("Verbose mode enabled.")
else:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.ERROR)


# Determine target MAC, CLI flag takes precedence over environment variable
candidate_mac = args.mac_address or os.getenv("RUUVITAG_MAC")

if not candidate_mac:
    log.critical("RUUVITAG_MAC environment variable not found and --mac-address not provided.")
    sys.exit(1)

if not re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", candidate_mac):
    log.critical("Invalid MAC-address provided.")
    sys.exit(1)

TARGET_MAC = candidate_mac

async def main():              
    try:
        async for mac, data in RuuviTagSensor.get_data_async(macs=TARGET_MAC):
            time = datetime.now(timezone.utc).isoformat()
            if args.delay:
                log.info(f"Sleeping for {int(args.delay)} milliseconds")
                timer.sleep(int(args.delay)/1000)
            if any(data[i] is None or data[i] == "" for i in data):
                log.error("Ruuvitag returned one or more null values. Discarding data...")
                log.error(data)
                continue
            tempc = data['temperature']         # Temperature in Celsius
            humidity = data['humidity']         # Humidity in Percentage
            pressure = data['pressure']         # Pressure in hPa
            battery = data['battery']           # Voltage in Millivolts
            log.info(f"Ruuvitag ({mac}) returned:\nTemperature: {tempc} Celsius\nHumidity: {humidity} %\nPressure: {pressure} hPa\nBattery: {battery} mV\n")
            write_to_db(time,mac,tempc,humidity,pressure,battery)
            if bool(args.run_once) == True:     # Break out of loop if -s / -run-once argument is set
                break
    except Exception as e:
        log.error(f"Error: {e}")

def emulate_main():
    if not args.delay:
        log.critical("Please specify a delay using the -d / --delay flags.")
        sys.exit(1)     # EXIT_FAILURE
    try:
        while True:
            log.info(f"Sleeping for {int(args.delay)} milliseconds")
            timer.sleep(int(args.delay)/1000)
            time = datetime.now(timezone.utc).isoformat()
            mac = "FF:FF:FF:FF:FF:FF"                               # Obviously fake MAC for discriminatory purposes
            tempc = round(float(rand.uniform(20,24)),2)             # Temperature in Celsius
            humidity = round(float(rand.uniform(20,24)),2)          # Humidity in Percentage
            pressure = round(float(rand.uniform(800,1200)),2)       # Pressure in hPa
            battery = int(rand.randint(1950,3250))                  # Voltage in Millivolts
            log.info(f"Ruuvitag ({mac}) returned:\nTemperature: {tempc} Celsius\nHumidity: {humidity} %\nPressure: {pressure} hPa\nBattery: {battery} mV\n")
            write_to_db(time,mac,tempc,humidity,pressure,battery)
            if bool(args.run_once) == True:     # Break out of loop if -s / -run-once argument is set
                break
    except Exception as e:
        log.error(f"Error: {e}")
    
def connect_to_db():
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        return con, cur
    except Exception as e:
        log.critical("Could not connect to database. Exiting...")
        sys.exit(1) # EXIT_FAILURE
    
def init_db():
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        con, cur = connect_to_db()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,
            mac TEXT NOT NULL,
            tempc REAL NOT NULL,
            humidity REAL NOT NULL,
            pressure REAL NOT NULL,
            battery REAL NOT NULL)
            ''')
        con.commit()
        con.close()
        log.info(f'Created {DB_PATH}')
    except Exception as e:
        log.critical(f"Could not initialize database. Exiting... {e}")
        sys.exit(1) # EXIT_FAILURE
    
def write_to_db(time, mac, tempc, humidity, pressure, battery):  
    con, cur = connect_to_db()
    cur.execute('INSERT INTO readings (time, mac, tempc, humidity, pressure, battery) VALUES (?, ?, ?, ?, ?, ?)', (time, mac, tempc, humidity, pressure, battery))
    con.commit()
    con.close()
    log.info("Wrote to database successfully.")
        
if __name__ == "__main__":
    if bool(args.emulate) != True and TARGET_MAC == None or TARGET_MAC == "":
        log.critical("TARGET_MAC not set, exiting!")
        sys.exit(1) # EXIT_FAILURE

    try:
        if os.path.isfile(DB_PATH) != True:
            log.error(f"Error: database not found at {DB_PATH}, creating it.")
            init_db() 
            
        if not args.emulate:
            asyncio.run(main())
        else:
            emulate_main()
            
    except KeyboardInterrupt:       # handle ctrl+c
        log.error("Interrupted.")
        sys.exit(130)   # EXIT_SIGINT 
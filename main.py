import asyncio
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import os.path
import sys
import logging as log
import argparse

os.chdir(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))        # Set working directory to script location

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")        # -v / --verbose for verbose logging
parser.add_argument("-d", "--debug", action="store_true", help="Debugging mode")        # -vvvv / --superverbosemode for debug logging
parser.add_argument("-s", "--run-once", action="store_true", help="Log data once.")     # -s / --run-once for single log
parser.add_argument("-a", "--mac-address", help="Use specific MAC-address")             # -s / --run-once for single log
args = parser.parse_args()

DB_PATH = Path('data/data.db')                  # Database location
os.environ["RUUVI_BLE_ADAPTER"] = "bleak"       # BLE adapter

# Configure logging once based on args
if args.debug:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)
    log.info("Debug mode enabled.")
elif args.verbose:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)
    log.info("Verbose mode enabled.")
else:
    log.basicConfig(format='', level=log.ERROR)

# Determine target MAC, CLI flag takes precedence over environment variable
try:
    TARGET_MAC = args.mac_address if args.mac_address else os.getenv("RUUVITAG_MAC")
except:
    log.critical("RUUVITAG_MAC environment variable not found and --mac-address not provided.")
    sys.exit(1)

async def main():              
    time = datetime.now(timezone.utc).isoformat()
    try:
        async for mac, data in RuuviTagSensor.get_data_async(macs=TARGET_MAC):
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

def connect_to_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    return con, cur
    
def init_db():
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
    
def write_to_db(time, mac, tempc, humidity, pressure, battery):  
    con, cur = connect_to_db()
    cur.execute('INSERT INTO readings (time, mac, tempc, humidity, pressure, battery) VALUES (?, ?, ?, ?, ?, ?)', (time, mac, tempc, humidity, pressure, battery))
    con.commit()
    con.close()
    log.info("Wrote to database successfully.")
        
if __name__ == "__main__":
    if TARGET_MAC == None or TARGET_MAC == "":
        log.critical("TARGET_MAC not set, exiting!")
        sys.exit(1) 
    try:
        if os.path.isfile(DB_PATH) != True:
            log.error(f"Error: database not found at {DB_PATH}, creating it.")
            init_db() 
        asyncio.run(main())
    except KeyboardInterrupt:       # handle ctrl+c
        log.error("Interrupted.")
        sys.exit(0) 
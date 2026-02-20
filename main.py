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

# Set working directory to script location
os.chdir(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))

# Variables
os.environ["RUUVI_BLE_ADAPTER"] = "bleak"   
TARGET_MAC = os.environ["RUUVITAG_MAC"]     # export RUUVITAG_MAC="CF:21:C3:AB:BD:C1" tai muu MAC-osoite
DB_PATH = Path('data/data.db')              # Database location

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")    # -v / --verbose for verbose logging
parser.add_argument("-vvvv", "--superverbosemode", action="store_true", help="SUPER VERBOSE mode (debugging)")    # -vvvv / --superverbosemode for debug logging
args = parser.parse_args()

if args.verbose:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)
    log.basicConfig(level=log.INFO)
    log.info("Verbose mode enabled.")
if args.superverbosemode:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)
    log.basicConfig(level=log.DEBUG)
    log.info("Super verbose mode enabled.")
else:
    log.basicConfig(format='', level=log.ERROR)
    

async def main():       
    time = datetime.now(timezone.utc).isoformat()
    try:
        async for mac, data in RuuviTagSensor.get_data_async():
            mac = TARGET_MAC                    # Ruuvitag MAC address
            tempc = data['temperature']         # Celsius
            humidity = data['humidity']         # Percentage
            pressure = data['pressure']         # hPa
            battery = data['battery']           # Millivolts
            log.info(f"{mac}, {tempc}c, {humidity}%, {pressure} hPa, {battery} mV")
            write_to_db(time,mac,tempc,humidity,pressure,battery)
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
    con.close
    log.info(f'Created {DB_PATH}')
    
def write_to_db(time, mac, tempc, humidity, pressure, battery):
    if os.path.isfile(DB_PATH) != True:     # Check for database (just in case)
        log.info("This should not run. Something has gone wrong. Attempting to fix it.")
        init_db()      
    con, cur = connect_to_db()
    cur.execute('INSERT INTO readings (time, mac, tempc, humidity, pressure, battery) VALUES (?, ?, ?, ?, ?, ?)', (time, mac, tempc, humidity, pressure, battery))
    con.commit()
    con.close()
    log.info("Wrote to database successfully.")
        
if __name__ == "__main__":
    try:
        if os.path.isfile(DB_PATH) != True:
            log.error(f"Error: database not found at {DB_PATH}, creating it.")
            init_db() 
        asyncio.run(main())
    except KeyboardInterrupt:       # handle ctrl+c
        log.error("Interrupted.")
        sys.exit(0)
    

# sqlite3 data/data.db "SELECT id, time, mac, tempc, humidity, pressure, battery FROM readings ORDER BY id DESC LIMIT 5;"



    
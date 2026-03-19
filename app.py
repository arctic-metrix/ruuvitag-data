import sqlite3
import logging as log
import argparse
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import os
import sys
import re

DB_PATH = Path('data/data.db')
TEMPLATE_PATH = 'templates/index.html'
app = Flask(__name__)
os.chdir(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
parser.add_argument("-vvvv", "--debug", action="store_true", help="Debugging mode")
parser.add_argument("-b", "--bind", help="Bind address")
parser.add_argument("-p", "--port", help="Bind port")
args = parser.parse_args()
    
if args.debug:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)
elif args.verbose:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)
else:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.ERROR)
    
if args.bind:
    if not re.match(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$", args.bind):
        log.critical("Valid IP address not provided.")
        sys.exit(1)
    else:
        HOST = args.bind
else:
    HOST = "0.0.0.0"

if args.port:
    if not 1 < int(args.port) < 65535:
        log.critical("Valid port not provided.")
        sys.exit(1)
    else:
        PORT = int(args.port)
else:
    PORT = 8080
    
def query_readings(limit: int = 60):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute('''
        SELECT time, mac, tempc, humidity, pressure, battery
        FROM readings
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))
    rows = cur.fetchall()
    con.close()
    
    return [
        {
            'ts_unix': r['time'],
            'mac': r['mac'],
            'temperature': r['tempc'],
            'humidity': r['humidity'],
            'pressure': r['pressure'],
            'battery_voltage': r['battery'], 
            'movement_counter': None,
            'measurement_sequence_number': None
        }
        for r in rows
    ]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/latest')
def api_latest():
    data = query_readings(limit=1)
    if not data:
        return jsonify({'error': 'No data found'}), 404
    return jsonify(data[0])

@app.route('/api/history')
def api_history():
    limit = int(request.args.get('limit', 60))
    data = query_readings(limit=limit)
    return jsonify(data)

if __name__ == "__main__":    
    app.run(host=HOST, port=PORT)
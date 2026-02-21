import sqlite3
import logging as log
import argparse
from pathlib import Path
from flask import Flask, render_template, jsonify, request
import os

DB_PATH = Path('data/data.db')
TEMPLATE_PATH = ('templates/index.html')
app = Flask(__name__)
os.chdir(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))        # Set working directory to script location

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")        # -v / --verbose for verbose logging
parser.add_argument("-vvvv", "--debug", action="store_true", help="Debugging mode")     # -vvvv / --debug for debug logging
args = parser.parse_args()

# Configure logging once based on args
if args.debug:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.DEBUG)
    log.info("Debug mode enabled.")
elif args.verbose:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.INFO)
    log.info("Verbose mode enabled.")
else:
    log.basicConfig(format='%(levelname)s: %(message)s', level=log.ERROR)
    
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
            'time': r['time'],
            'mac': r['mac'],
            'tempc': r['tempc'],
            'humidity': r['humidity'],
            'pressure': r['pressure'],
            'battery': r['battery']
        }
        for r in rows
    ]

@app.route('/')
def index():
    readings = query_readings(limit=60)
    return render_template('index.html', readings=readings)

@app.route('/api/readings')
def api_readings():
    limit = int(request.args.get('limit', 60))
    rows = query_readings(limit=limit)
    data = [
        {'time': r['time'], 
         'mac': r['mac'], 
         'tempc': r['tempc'], 
         'humidity': r['humidity'], 
         'pressure': r['pressure'], 
         'battery': r['battery']}
        for r in reversed(rows)
    ]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'ruuvi.sqlite3'
TEAM_PATH = BASE_DIR / 'team.json'

app = Flask(__name__)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_database() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS ruuvi_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_unix REAL NOT NULL,
                mac TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                acceleration_x REAL,
                acceleration_y REAL,
                acceleration_z REAL,
                battery_voltage REAL,
                tx_power INTEGER,
                movement_counter INTEGER,
                measurement_sequence_number INTEGER,
                data_format INTEGER,
                raw_json TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_ruuvi_mac_ts
            ON ruuvi_measurements(mac, ts_unix);
            """
        )

        row_count = conn.execute('SELECT COUNT(*) AS c FROM ruuvi_measurements').fetchone()['c']
        if row_count == 0:
            now = int(time.time())
            seed_rows: list[tuple[Any, ...]] = []
            for i in range(24):
                t = now - (23 - i) * 300
                seed_rows.append(
                    (
                        t,
                        'AA:BB:CC:DD:EE:FF',
                        round(22.1 + ((i % 5) - 2) * 0.35, 2),
                        round(41.0 + ((i % 4) - 1) * 1.4, 2),
                        round(1008.0 + ((i % 6) - 2) * 0.8, 2),
                        0.0,
                        0.0,
                        0.0,
                        2.91,
                        4,
                        i,
                        i,
                        5,
                        json.dumps({'demo': True, 'index': i}),
                    )
                )

            conn.executemany(
                """
                INSERT INTO ruuvi_measurements (
                    ts_unix, mac, temperature, humidity, pressure,
                    acceleration_x, acceleration_y, acceleration_z,
                    battery_voltage, tx_power, movement_counter,
                    measurement_sequence_number, data_format, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                seed_rows,
            )
        conn.commit()


def load_team() -> list[dict[str, Any]]:
    if not TEAM_PATH.exists():
        return []
    with TEAM_PATH.open('r', encoding='utf-8') as f:
        return json.load(f)


@app.route('/')
def index():
    return render_template('index.html', team=load_team())


@app.route('/api/latest')
def api_latest():
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT ts_unix, mac, temperature, humidity, pressure,
                   battery_voltage, movement_counter, measurement_sequence_number
            FROM ruuvi_measurements
            ORDER BY ts_unix DESC
            LIMIT 1
            """
        ).fetchone()

    if row is None:
        return jsonify({'error': 'No data found'}), 404

    return jsonify(dict(row))


@app.route('/api/history')
def api_history():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT ts_unix, mac, temperature, humidity, pressure, battery_voltage
            FROM ruuvi_measurements
            ORDER BY ts_unix DESC
            LIMIT 20
            """
        ).fetchall()

    result = [dict(row) for row in reversed(rows)]
    return jsonify(result)


@app.route('/api/team')
def api_team():
    return jsonify(load_team())


if __name__ == '__main__':
    ensure_database()
    app.run(debug=True)

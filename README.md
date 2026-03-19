# ruuvitag-data

Lightweight logger for RuuviTag BLE sensors that stores readings into a local SQLite database.

**Features**
- Read temperature, humidity, pressure and battery values from RuuviTag sensors via BLE
- Store readings in data/data.db (SQLite)
- CLI flags for verbosity, single-shot logging, emulation, and specifying MAC address

**Prerequisites**
- Python 3.8+
- `ruuvitag_sensor` package (install with `pip install ruuvitag_sensor`)
- On some systems you may need `bleak` for BLE support: `pip install bleak`

**Install required packages**
```bash 
pip install -r requirements.txt
```

Data Logger Usage
-----------------
Run the logger script from the project root. By default the script reads the MAC address from the
`RUUVITAG_MAC` environment variable. Use `--mac-address` (or `-a`) to override.

Basic example (use env var):
```bash
export RUUVITAG_MAC="CF:21:C3:AB:BD:C1"
python main.py
```

Run once (single reading):
```bash
python main.py -s -a "CF:21:C3:AB:BD:C1"
```

Emulate readings (generates pseudorandom plausible sensor values):
```bash
python main.py -e -d 1000
```

Examples for logging flags and delay:
```bash
python main.py -v -a "CF:21:C3:AB:BD:C1"        # verbose (info)
python main.py --debug -a "CF:21:C3:AB:BD:C1"   # debug (more verbose)
python main.py -e -d 2000                        # emulate, delay 2000 ms between readings
```

Web Server Usage
----------------
You can view and access the logged data via a simple Flask web server:

```bash
python server.py
```

By default, the server runs on all interfaces at port 8080:
- Web UI: http://127.0.0.1:8080/
- API: http://127.0.0.1:8080/api/readings?limit=60

You can use the `-v` or `-vvvv` flags for verbose or debug logging:
```bash
python server.py -v
python server.py -vvvv
```

You can also specify a host to bind to and a port to use
```bash
# Bind to 192.168.6.7:6767
python server.py -b 192.168.6.7 -p 6767     

# Binds to 0.0.0.0:6767
python server.py -p 6767     
```
#### API Endpoint

- `/api/readings?limit=N` — Returns the latest N readings as JSON. Each reading contains:
	- `time`: ISO timestamp
	- `mac`: Sensor MAC address
	- `tempc`: Temperature in Celsius
	- `humidity`: Relative humidity (%)
	- `pressure`: Pressure (hPa)
	- `battery`: Battery voltage (mV)

#### Web UI

- The root page `/` displays the latest readings in a table.

Flags for server.py:
-----
| Flag | Description |
| --- | ----------- |
| `-v`, `--verbose` | Enables verbose logging (`log.info`) |
| `-vvvv`, `--debug` | Enables debug logging (`log.debug`) (the CLI uses `-vvvv` as the short form) |
| `-b`, `--bind [IP ADDRESS]` | Binds to IP address (defaults to 0.0.0.0 if not set) |
| `-p`, `--port [PORT]` | Specify port (defaults to 8080) |

Flags for main.py:
-----
| Flag | Description |
| --- | ----------- |
| `-v`, `--verbose` | Enables verbose logging (`log.info`) |
| `-vvvv`, `--debug` | Enables debug logging (`log.debug`) (the CLI uses `-vvvv` as the short form) |
| `-s`, `--run-once` | Take a single reading and exit |
| `-a`, `--mac-address [MAC]` | Specify MAC address (overrides `RUUVITAG_MAC`) |
| `-e`, `--emulate` | Generate plausible pseudorandom readings (use with `-d` for delay) |
| `-d`, `--delay [MS]` | Delay between readings in milliseconds (required for emulation) |

Environment variables
---------------------
- `RUUVITAG_MAC` — default MAC address to read from (overridden by `--mac-address`)
- `RUUVI_BLE_ADAPTER` — adapter used by `ruuvitag_sensor` (the script sets this to `bleak`)

Database
--------
Readings are stored in `data/data.db` in a table named `readings` with columns:
`id, time, mac, tempc, humidity, pressure, battery`.

Notes
-----
- The script will create the `data` directory and the SQLite database file automatically if missing.
- When using `--emulate`, specify `--delay` (milliseconds) so the script can sleep between entries.

Troubleshooting
---------------
- If you get an error about `RUUVITAG_MAC` not being set, either export the variable or use `-a`.
- If BLE scanning fails, ensure your system BLE stack is working and that `bleak` (or your adapter backend) is available.

License
-------
See the `LICENSE` file in this repository.


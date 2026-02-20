# ruuvitag-data

Lightweight logger for RuuviTag BLE sensors that stores readings into a local SQLite database.

**Features**
- Read temperature, humidity, pressure and battery values from RuuviTag sensors via BLE
- Store readings in `data/data.db` (SQLite)
- CLI flags for verbosity, single-shot logging, and specifying MAC address

**Prerequisites**
- Python 3.8+
- `ruuvitag_sensor` package (install with `pip install ruuvitag_sensor`)

Usage
-----
Run the script from the project root. By default the script reads the MAC address from the
`RUUVITAG_MAC` environment variable. Use `--mac-address` to override.

Basic example (use env var):
```bash
export RUUVITAG_MAC="CF:21:C3:AB:BD:C1"
python main.py
```

Run once (single reading):
```bash
python main.py -s -a "CF:21:C3:AB:BD:C1"
```

Enable verbose or debug logging:
```bash
python main.py -v -a "CF:21:C3:AB:BD:C1"
python main.py -d -a "CF:21:C3:AB:BD:C1"
```

Flags
-----
| Flag | Description |
| --- | ----------- |
| `-v`, `--verbose` | Enables verbose logging (`log.info`) |
| `-d`, `--debug` | Enables debug logging (`log.debug`) |
| `-s`, `--run-once`| Take a single reading and exit |
| `-a`, `--mac-address [MAC]` | Specify MAC address (overrides `RUUVITAG_MAC`) |

Environment variables
---------------------
- `RUUVITAG_MAC` — default MAC address to read from (overridden by `--mac-address`)
- `RUUVI_BLE_ADAPTER` — adapter used by `ruuvitag_sensor` (the script sets this to `bleak`)

Database
--------
Readings are stored in `data/data.db` in a table named `readings` with columns:
`id, time, mac, tempc, humidity, pressure, battery`.

Troubleshooting
---------------
- If you get an error about `RUUVITAG_MAC` not being set, either export the variable or use `-a`.
- Use `-d` to see detailed logs when diagnosing BLE/connectivity issues.

License
-------
See the `LICENSE` file in this repository.


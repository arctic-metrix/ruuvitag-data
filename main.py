import asyncio
import os

# Must be set before importing ruuvitag_sensor on Linux
os.environ["RUUVI_BLE_ADAPTER"] = "bleak"
TARGET_MAC = os.environ["RUUVITAG_MAC"]

from ruuvitag_sensor.ruuvi import RuuviTagSensor

async def main():
    # Streams data indefinitely from all detected RuuviTags
    async for mac, data in RuuviTagSensor.get_data_async(macs=[TARGET_MAC]):
        print(f"MAC: {mac}")
        print(f"  Temperature:  {data['temperature']} °C")
        print(f"  Humidity:     {data['humidity']} %")
        print(f"  Pressure:     {data['pressure']} hPa")
        print(f"  Acc X/Y/Z:    {data['acceleration_x']}/{data['acceleration_y']}/{data['acceleration_z']} mG")
        print(f"  Battery:      {data['battery']} mV")
        print()

if __name__ == "__main__":
    asyncio.run(main())

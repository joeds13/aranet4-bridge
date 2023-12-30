import os
import time
import sys
from signal import signal, SIGINT, SIGTERM
from datetime import datetime

from aranet4 import client
from aranet4.client import Status
from prometheus_client import Enum, Info, Gauge, start_http_server

# Output example
# CurrentReading(name='Aranet4 24ED2',
#                version='v1.4.14',
#                temperature=19.7,
#                humidity=38,
#                pressure=982.6,
#                co2=791,
#                battery=95,
#                status=<Status.GREEN: 1>,
#                status_t=-1,
#                status_h=-1,
#                interval=120,
#                ago=4,
#                stored=3658,
#                counter=-1)

i_aranet4 = Info("aranet4", "Device info")
g_battery_percentage = Gauge("battery_precentage", "Battery life as a percentage")
g_temperature_celcius = Gauge("temperature_celcius", "Temperature in Celcius")
g_humidity_percentage = Gauge("humidity_percentage", "Humidity percentage")
g_pressure_hpa = Gauge("pressure_hpa", "Pressure in Hectopascals")
g_co2_ppm = Gauge("co2_ppm", "CO2 in Parts per Million")
e_co2_status = Enum("co2_status", "CO2 status", states=[e.name for e in Status])


def get_readings(sensor_bt_mac: str) -> None:
    # TODO: this blocks, consider async
    current = client.get_current_readings(sensor_bt_mac)
    print(f"{datetime.utcnow()}: Reading from {current.name}")

    i_aranet4.info({"version": current.version, "name": current.name})

    g_battery_percentage.set(str(current.battery))
    g_temperature_celcius.set(current.temperature)
    g_humidity_percentage.set(current.humidity)
    g_pressure_hpa.set(current.pressure)
    g_co2_ppm.set(current.co2)
    e_co2_status.state(Status(current.status).name)


def main() -> None:
    sensor_bt_mac = os.getenv("SENSOR_BT_MAC", "C1:C2:30:EE:A8:72")

    # get some readings before starting the server, to avoid an empty scrape resetting metrics
    get_readings(sensor_bt_mac)

    # start the metrics server
    start_http_server(8000)

    # loop forever reading from the sensor every 30 seconds
    # TODO: handle exit code cleanly
    while True:
        # TODO: use interval/ago values to wait optimally
        time.sleep(30)
        # TODO: handle read exceptions
        get_readings(sensor_bt_mac)


def exit_handler(sig, frame) -> None:
    print(f"{datetime.utcnow()}: Recieved exit code {str(sig)}")
    sys.exit(0)


if __name__ == "__main__":
    print(f"{datetime.utcnow()}: Starting...")
    signal(SIGINT, exit_handler)
    signal(SIGTERM, exit_handler)
    main()

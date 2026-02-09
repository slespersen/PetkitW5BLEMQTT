#!/usr/bin/env python3
import asyncio
import subprocess
import sys
import time
import logging
import os
from bleak import BleakScanner

PETKIT_PREFIXES = ("W4", "W5", "CTW2")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - Supervisor - %(levelname)s - %(message)s"
)
logger = logging.getLogger("PetkitSupervisor")

# Resolve absolute path to main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PATH = os.path.join(BASE_DIR, "main.py")


async def scan_petkit_devices():
    logger.info("Scanning for Petkit BLE devices...")
    devices = await BleakScanner.discover()

    found = {}
    for dev in devices:
        if dev.name and any(prefix in dev.name for prefix in PETKIT_PREFIXES):
            logger.info(f"Found Petkit device: {dev.name} ({dev.address})")
            found[dev.address] = dev.name

    return found


def start_worker(address, mqtt_args):
    """Start a worker process running main.py for a specific device."""
    cmd = [
        sys.executable,
        MAIN_PATH,                     # <-- FIXED PATH
        "--address", address,
        "--logging_level", "INFO"
    ]

    if mqtt_args:
        cmd.append("--mqtt")
        if mqtt_args.get("broker"):
            cmd += ["--mqtt_broker", mqtt_args["broker"]]
        if mqtt_args.get("port"):
            cmd += ["--mqtt_port", str(mqtt_args["port"])]
        if mqtt_args.get("username"):
            cmd += ["--mqtt_user", mqtt_args["username"]]
        if mqtt_args.get("password"):
            cmd += ["--mqtt_password", mqtt_args["password"]]

    logger.info(f"Launching worker for {address}: {' '.join(cmd)}")
    return subprocess.Popen(cmd)


async def supervisor(mqtt_args):
    workers = {}

    while True:
        try:
            found = await scan_petkit_devices()

            # Start workers for new devices
            for address in found:
                if address not in workers:
                    workers[address] = start_worker(address, mqtt_args)
                    time.sleep(1)

            # Restart crashed workers
            for address, proc in list(workers.items()):
                if proc.poll() is not None:
                    logger.warning(
                        f"Worker for {address} exited with code {proc.returncode}, restarting..."
                    )
                    workers[address] = start_worker(address, mqtt_args)

            await asyncio.sleep(10)

        except KeyboardInterrupt:
            logger.info("Supervisor interrupted, shutting down workers...")
            for proc in workers.values():
                proc.terminate()
            for proc in workers.values():
                proc.wait()
            break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Petkit Supervisor")
    parser.add_argument("--mqtt", action="store_true")
    parser.add_argument("--mqtt_broker", type=str)
    parser.add_argument("--mqtt_port", type=int, default=1883)
    parser.add_argument("--mqtt_user", type=str)
    parser.add_argument("--mqtt_password", type=str)

    args = parser.parse_args()

    mqtt_args = None
    if args.mqtt:
        mqtt_args = {
            "broker": args.mqtt_broker,
            "port": args.mqtt_port,
            "username": args.mqtt_user,
            "password": args.mqtt_password,
        }

    asyncio.run(supervisor(mqtt_args))

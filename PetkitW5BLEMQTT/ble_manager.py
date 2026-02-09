from bleak import BleakScanner, BleakClient
from .constants import Constants
from .utils import Utils
from .device import Device
import asyncio
import logging

class BLEManager:
    def __init__(self, event_handler, commands, logger, callback=None):
        self.connected_devices = {}
        self.available_devices = {}
        self.connectiondata = {}
        self.logger = logger
        self.queue = asyncio.Queue(10)
        self.callback = callback
        self.device = False
        self.event_handler = event_handler
        self.commands = commands

    async def scan(self):
        self.logger.info("Scanning for Petkit BLE devices...")
        devices = await BleakScanner.discover()
        self.available_devices = {dev.address: dev for dev in devices if dev.name and ("W4" in dev.name or "W5" in dev.name or "CTW2" in dev.name)}
        for address, device in self.available_devices.items():
            self.logger.info(f"Found device: {device.name} ({address})")
            self.connectiondata[address] = device
        return self.available_devices

    async def connect_device(self, address):
        if address in self.available_devices:
            self.logger.info(f"Connecting to {address}...")
            client = BleakClient(address, timeout = 65.0)
            await client.connect()
            
            self.connected_devices[address] = client
            self.logger.info(f"Connected to {address}")
            await self.start_notifications(address, Constants.READ_UUID)
            return True
        else:
            self.logger.error(f"Device {address} not found")
            return False

    async def disconnect_device(self, address):
        if address in self.connected_devices:
            self.logger.info(f"Disconnecting from {address}...")
            client = self.connected_devices[address]
            
            if client.is_connected:
                await client.stop_notify(Constants.READ_UUID)
            
            await client.disconnect()
            del self.connected_devices[address]
            self.logger.info(f"Disconnected from {address}")
            return True
        else:
            self.logger.error(f"Device {address} not connected")
            return False

    async def read_characteristic(self, address, characteristic_uuid):
        if address in self.connected_devices:
            self.logger.info(f"Reading characteristic {characteristic_uuid} from {address}")
            client = self.connected_devices[address]
            data = await client.read_gatt_char(characteristic_uuid)
            self.logger.info(f"Read data: {data}")
            return data
        else:
            self.logger.error(f"Device {address} not connected")
            return None

    async def write_characteristic(self, address, characteristic_uuid, data):
        if address in self.connected_devices:
            client = self.connected_devices[address]
        
            try:
                self.logger.info(f"Writing to characteristic {characteristic_uuid} on {address}")
        
                await asyncio.wait_for(
                    client.write_gatt_char(characteristic_uuid, data),
                    timeout=5.0
                )
        
                self.logger.info("Write complete")
                return True
        
            except asyncio.TimeoutError:
                self.logger.error(f"Write timeout on {address}, reconnecting...")
                await self.disconnect_device(address)
                await asyncio.sleep(1)
                await self.connect_device(address)
                return False
        
            except Exception as e:
                self.logger.error(f"Write failed: {e}")
                return False

        else:
            self.logger.error(f"Device {address} not connected")
            return False

    async def start_notifications(self, address, characteristic_uuid):
        if address in self.connected_devices:
            self.logger.info(f"Starting notifications for {characteristic_uuid} on {address}")
            client = self.connected_devices[address]
            await client.start_notify(characteristic_uuid, self._handle_notification_wrapper)
            self.logger.info(f"Notifications started for {characteristic_uuid} on {address}")
            return True
        else:
            self.logger.error(f"Device {address} not connected")
            return False

    async def _handle_notification_wrapper(self, sender, data):
        await self.event_handler.handle_notification(sender, data)

    async def stop_notifications(self, address, characteristic_uuid):
        if address in self.connected_devices:
            self.logger.info(f"Stopping notifications for {characteristic_uuid} on {address}")
            client = self.connected_devices[address]
            await client.stop_notify(characteristic_uuid)
            self.logger.info(f"Notifications stopped for {characteristic_uuid} on {address}")
            return True
        else:
            self.logger.error(f"Device {address} not connected")
            return False

    async def heartbeat(self, interval):
        while True:
            for address in list(self.connected_devices.keys()):
                try:
                    await self.commands.get_battery() # To update voltage
                    await self.commands.get_device_update()
                    
                    if self.queue.qsize() > 10: 
                        raise Exception("Queue size over threshold. Disconnecting...")
                    
                    await asyncio.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Error during heartbeat: {e}")
                    self.logger.info(f"Attempting to reconnect to {address}")
                    await self.disconnect_device(address)
                    await asyncio.sleep(5)
                    await self.connect_device(address)

    async def message_consumer(self, address, characteristic_uuid):
        while True:
            if not self.connected_devices.get(address):
                self.logger.warning(f"Device {address} not connected. Attempting to reconnect...")
                await self.connect_device(address)
                await asyncio.sleep(1)
                continue

            message = await self.queue.get()
            await self.write_characteristic(address, characteristic_uuid, message)
            self.queue.task_done()

    async def message_producer(self, message):
        await self.queue.put(message)

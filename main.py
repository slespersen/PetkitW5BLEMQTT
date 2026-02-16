import argparse
import asyncio
import logging
from PetkitW5BLEMQTT import BLEManager, Constants, Device, EventHandlers, Commands, Logger, MQTTClient, MQTTCallback, MQTTPayloads, Utils

class Manager:
    def __init__(self, address, mqtt_enabled=False, mqtt_settings=None, logging_level=logging.INFO):
        self.address = address
        self.device = Device(self.address)
        
        self.setup_logging(logging_level)
        self.logger = logging.getLogger(f"PetkitW5BLEMQTT-{self.device.mac_readable}")
        debug = logging_level == logging.DEBUG  # Determine if debug logging is enabled

        # Correct order of instantiation
        self.commands = Commands(ble_manager=None, device=self.device, logger=self.logger)
        self.event_handlers = EventHandlers(device=self.device, commands=self.commands, logger=self.logger)
        self.ble_manager = BLEManager(event_handler=self.event_handlers, commands=self.commands, logger=self.logger)
        self.ble_manager.manager = self
        
        # Update ble_manager in commands now that it is created
        self.commands.ble_manager = self.ble_manager
        
        self.mqtt_client = None
        self.mqtt_callback = None
        self.mqtt_payloads = None

        if mqtt_enabled and mqtt_settings:
            self.mqtt_client = MQTTClient(logger=self.logger, **mqtt_settings)
            self.mqtt_client.connect()
            self.event_handlers.callback = self.mqtt_client.publish_state

    def setup_logging(self, logging_level):
        logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    async def run(self, address):
        await self.ble_manager.scan()
        
        self.logger.info(f"Connecting...")
        
        if await self.ble_manager.connect_device(address):
            self.logger.info(f"Connected.")
            
            # Start the producer and consumer tasks
            consumer = asyncio.create_task(self.ble_manager.message_consumer(address, Constants.WRITE_UUID))

            # Init the device
            self.commands.init_device_data()
            
            try:
                # Connect to the device
                await self.commands.init_device_connection()
                
                # Initialize the heartbeat
                heartbeat = asyncio.create_task(self.ble_manager.heartbeat(60))
                
                if self.mqtt_client and self.mqtt_client.connected:                    
                    # Setup the MQTT payloads
                    self.mqtt_payloads = MQTTPayloads(device=self.device)
                    
                    # Tell MQTTClient which identifier to use for availability 
                    self.mqtt_client.set_identifier(self.device.mac_readable)
                    
                    self.logger.info(f"Sending payloads...")
                    
                    # Setup the MQTT callback function
                    self.mqtt_callback = MQTTCallback(device=self.device, commands=self.commands)
                    
                    # Generate discovery payloads
                    discovery_payloads = self.mqtt_payloads.discovery()
                    
                    # Post discovery payloads
                    self.mqtt_client.publish_discovery(discovery_payloads)
                    
                    # Subscribe to the command topic
                    self.mqtt_client.subscribe(f"PetkitMQTT/{self.device.mac_readable}/command")
                    
                    # Setup the callback function for handling messages
                    self.mqtt_client.set_on_message(self.mqtt_callback.delegate)

                    # Post online to availability topic
                    self.mqtt_client.publish_availability(self.device.mac_readable, "online")
                while True:
                    await asyncio.sleep(1)  # Example interval for ad-hoc message sending

            except KeyboardInterrupt:
                # Handling cleanup on keyboard interrupt
                self.logger.info("Interrupted, cleaning up...")            
                
                # Wait for queue to be empty and disconnect the device
                await self.ble_manager.queue.join()
                await self.ble_manager.disconnect_device(address)
            finally:
                if self.mqtt_client:
                    self.mqtt_client.publish_availability(self.device.mac_readable, "offline")
                    self.mqtt_client.disconnect()

    async def restart_run(self, address = None):
        if address is None:
            address = self.address
        
        self.logger.info("Restarting run function due to inactivity.")

        # Reset initialization_state and software_version
        self.device.initialization_state = False
        self.device.info = {'software_version': None}
        
        await self.run(address)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BLE Manager")
    parser.add_argument("--address", type=str, required=True, help="BLE device address")
    parser.add_argument("--mqtt", action='store_true', help="Enable MQTT")
    parser.add_argument("--mqtt_broker", type=str, help="MQTT broker address")
    parser.add_argument("--mqtt_port", default=1883, type=int, help="MQTT broker port")
    parser.add_argument("--mqtt_user", type=str, help="MQTT username")
    parser.add_argument("--mqtt_password", type=str, help="MQTT password")
    parser.add_argument("--logging_level", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    args = parser.parse_args()

    mqtt_settings = {
        "client_id": f"PetkitW5BLEMQTTClient-{args.address.replace(':','')}",
        "broker": args.mqtt_broker,
        "port": args.mqtt_port,
        "username": args.mqtt_user,
        "password": args.mqtt_password
    } if args.mqtt else None

    logging_level = getattr(logging, args.logging_level.upper(), logging.INFO)

    manager = Manager(args.address, mqtt_enabled=args.mqtt, mqtt_settings=mqtt_settings, logging_level=logging_level)
    asyncio.run(manager.run(args.address))
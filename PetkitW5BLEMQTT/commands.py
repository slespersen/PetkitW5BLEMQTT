import json
import asyncio
from .utils import Utils

class Commands:
    def __init__(self, ble_manager, device, logger):
        self.ble_manager = ble_manager
        self.device = device
        self.logger = logger  # Use the centralized logger
        self.sequence = 0
        
    def increment_sequence(self):
        self.sequence += 1
        
        # If sequence is too large, we'll reset
        if self.sequence > 255:
            self.sequence = 0
    
    def init_device_data(self):
        connectiondata = self.ble_manager.connectiondata[self.device.mac].details
        self.device.status = {"rssi": connectiondata['props'].get('RSSI', 0)}
        
        discovered_bytes = Utils.bytes_to_unsigned_integers(Utils.combine_byte_arrays(connectiondata['props']['ServiceData']))
        device_integer_identifier = discovered_bytes[5]

        self.logger.debug(f"Received ServiceData {discovered_bytes}")
        
        device_properties = Utils.get_device_properties(device_integer_identifier)
        
        self.device.name = device_properties['name']
        self.device.name_readable = device_properties['name'].replace("_", " ") # Replace _ with space
        self.device.product_name = device_properties['product_name']
        self.device.device_type = device_properties['device_type']
        self.device.type_code = device_properties['type_code']
        self.device.alias = device_properties['alias']
    
    async def init_device_connection(self):
        # Basically this function secures the sequence
        # of which we're sending the commands.
        # At the same time, we're ensuring we're getting
        # the necessary parameters registered - e.g. serial
        await self.get_device_details()
        await asyncio.sleep(1.5)
        
        await self.init_device()
        
        await self.get_device_sync()
        await asyncio.sleep(0.75)
        await self.set_datetime()
        await asyncio.sleep(0.75)
        
        while self.device.serial in "Uninitialized" or self.device.serial == 0:
            await self.get_device_details()
            await asyncio.sleep(1.5)
        
        if not self.device.device_initialized:
            await self.init_device()
            await asyncio.sleep(3.0)
            
            await self.ble_manager.disconnect_device(self.device.mac)
            await asyncio.sleep(1.0)
            await self.ble_manager.connect_device(self.device.mac)
            await asyncio.sleep(1.0)
            await self.init_device_connection()
        
        await self.get_device_info()
        await asyncio.sleep(0.75)
        await self.get_device_type()
        await asyncio.sleep(0.75)
        await self.get_battery()
        await asyncio.sleep(0.75)
        await self.get_device_state()
        await asyncio.sleep(0.75)
        await self.get_device_config()

    async def get_battery(self):
        cmd = 66                            # Command for getting device details
        type = 1                            # Sending 1
        seq = self.sequence                 # Example sequence number       
        data = [0, 0]                       # Placeholders
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return

    async def init_device(self):
        cmd = 73                            # Command for getting device details
        type = 1                            # Sending 1
        seq = self.sequence                 # Example sequence number       

        self.logger.info(f"Initializing device.")
        # In case you initialize the device using this class
        # the device_id will be erased after CMD 73
        # there seems to be somekind of validation of device_id vs secret
        # Should you want to control the device through 
        # the Petkit app, of some strange reason you will need to power cycle the device

        # Reverse the device_id_bytes array
        # replace the last two zeroes with 13 37 
        # and pad the array with zeroes to use as secret
        self.secret = Utils.pad_array(Utils.replace_last_two_if_zero(Utils.reverse_unsigned_array(self.device.device_id_bytes)), 8)
        
        # Pad the device_id_bytes with zeroes
        device_id = Utils.pad_array(self.device.device_id_bytes, 8)
        
        data = [0, 0] + device_id + self.secret    # Placeholders
        self.logger.debug(f"Device ID: {device_id}")
        self.logger.debug(f"Secret: {self.secret}")
        self.logger.debug(f"Data: {data}")
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return

    async def set_datetime(self):
        cmd = 84                            # Command for getting device details
        type = 1                            # Sending 1
        seq = self.sequence                 # Example sequence number       
        data = Utils.time_in_bytes()        # Datetime data
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return

    async def get_device_sync(self):
        cmd = 86                            # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
    
        self.logger.info(f"Awaiting device synchronization.")
        
        #data = [0, 0, 253, 54, 124, 210, 241, 44]   # What's going on here?
        data = [0, 0] + self.secret         # What's going on here?
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return

    async def get_device_info(self):
        cmd = 200                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [] 
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return
        
    async def get_device_type(self):
        cmd = 201                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [] 
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return
        
    async def get_device_state(self):
        cmd = 210                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [0, 0] 
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return
        
    async def get_device_config(self):
        cmd = 211                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [0, 0] 
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return

    async def get_device_details(self):    
        self.logger.info(f"Getting device details.")
    
        if self.device.device_id:
            return
        
        cmd = 213                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [0, 0]                       # No additional data for this command
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return
    
    # Not used -- maybe never
    async def set_light_setting(self):
        cmd = 215                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [0]                          # 0 resets it

        return

    # Not used -- maybe never
    async def set_dnd_setting(self):
        cmd = 216                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [0]                          # 0 resets it

        return

    async def set_device_mode(self, state, mode):
        cmd = 220                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [state, mode]                # State 1 for on, 0 for off - Mode 1 for normal, 2 for smart
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return

    #async def set_device_config(self, smart_time_on, smart_time_off, led_switch, led_brightness, led_light_time_on_1, led_light_time_on_2, led_light_time_off_1, led_light_time_off_2, do_not_disturb_switch, do_not_disturb_time_start_1, do_not_disturb_time_start_2, do_not_disturb_time_end_1, do_not_disturb_time_end_2, is_locked):
    async def set_device_config(self, data):
        cmd = 221                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number       
        #data = [smart_time_on, smart_time_off, led_switch, led_brightness, led_light_time_on_1, led_light_time_on_2, led_light_time_off_1, led_light_time_off_2, do_not_disturb_switch, do_not_disturb_time_start_1, do_not_disturb_time_start_2, do_not_disturb_time_end_1, do_not_disturb_time_end_2, is_locked]                # State 1 for on, 0 for off - Mode 1 for normal, 2 for smart
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return

    async def set_reset_filter(self):
        cmd = 222                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [0]                          # 0 resets it
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return

    # Not used -- maybe never
    async def set_updated_light(self):
        cmd = 225                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [0]                          # 0 resets it

        return

    # Not used -- maybe never
    async def set_updated_dnd(self):
        cmd = 226                           # Command for getting device details
        type = 1                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [0]                          # 0 resets it

        return
        
    async def get_device_update(self):
        cmd = 230                           # Command for getting device details
        type = 2                            # Type is 1 for sending - 2 for receiving
        seq = self.sequence                 # Example sequence number
        data = [1]                      # No additional data for this command
        
        bytes = Utils.build_command(seq, cmd, type, data)
        await self.ble_manager.message_producer(bytes)
        
        self.increment_sequence()
        
        self.logger.info(f"Queued command: {cmd}")
        return
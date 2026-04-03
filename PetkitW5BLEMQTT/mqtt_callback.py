import json
from .constants import Constants
from .utils import Utils

class MQTTCallback:
    def __init__(self, device=None, commands=None):
        self.device = device
        self.commands = commands
        self.logger = self.commands.logger # Hacky - but ... does it work? Passing logger to the class, will create duplicate log lines
    
    async def delegate(self, client, userdata, message):
        # Decode and convert the JSON string to a dictionary
        payload = json.loads(message.payload.decode("utf-8"))
        
        # Get the key of the payload
        key = next(iter(payload))
                
        # Retrieve the function from functions, based on the key retrieved
        value = payload[key]
        
        config_keys = [
            'do_not_disturb_switch', 
            'led_brightness', 
            'led_switch', 
            'smart_time_on', 
            'smart_time_off'
        ]
        
        number_keys = [
            'led_on', 
            'led_off', 
            'dnd_on', 
            'dnd_off'
        ]
        
        if key in config_keys:
            self.logger.info(f"Setting config {key} to {value}.")
            
            # retrieve current config
            config = self.device.config
            
            # update the current config with the new value
            config[key] = value
            
            # get all values without keys
            values = list(config.values())
            
            await self.commands.set_device_config(values)

        if key in number_keys:
            self.logger.info(f"Setting config {key} to {value}.")
            
            # convert the decimal value to timestamp
            decimal = Utils.decimal_to_time(value)
            
            # convert to minutes
            minutes = Utils.time_to_minutes(decimal)
            
            # retrieve the two bytes, containing the minutes
            byte1, byte2 = Utils.split_into_bytes(minutes)
            
            # create the new keys for updating the config
            label1 = f"{key}_byte1"
            label2 = f"{key}_byte2"
            
            # retrieve current config
            config = self.device.config
            
            # update the current config with the new values
            config[label1] = byte1
            config[label2] = byte2
            
            # get all values without keys
            values = list(config.values())
            
            await self.commands.set_device_config(values)
            
        if key == "state":
            self.logger.info(f"Setting state to {value}.")
            await self.commands.set_device_mode(value, self.device.status["mode"])
            
        if key == "mode":
            self.logger.info(f"Setting mode to {value}.")
            await self.commands.set_device_mode(self.device.status["power_status"], value)
            
        if key == "reset_filter":
            self.logger.info(f"Resetting filter.")
            await self.commands.set_reset_filter()
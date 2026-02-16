import asyncio
from .utils import Utils
from .constants import Constants

class Device:
    def __init__(self, address):
        self.device_initialized = 0
        self.device_id = 0
        self.device_id_bytes = []
        self.serial = "Uninitialized"
        self.secret = [0, 0, 0, 0, 0, 0, 13, 37]
        self.mac = address
        self.mac_readable = address.replace(":", "") # Replace : with nothing
        self.name = "Uninitialized"
        self.name_readable = "Uninitialized"
        self.product_name = "Uninitialized"
        self.alias = "Uninitialized"
        self.firmware = 0
        self.device_type = 0
        self.type_code = 0
        self.rssi = 0
        self._mac_readable = self.mac_readable
        self._name_readable = self.name_readable
        self._voltage = 0.0
        self._battery = 0
        self._low_battery = 0
        self._battery_working_time = 0
        self._battery_sleep_time = 0
        self._battery_time_on = 0
        self._battery_time_off = 0
        self._energy_consumed = 0
        self._filter_time_left = 0
        self._rssi = self.rssi
        self._supply_voltage = 0
        self._battery_voltage = 0
        self._battery_percentage = 0
        self._power_status = 0
        self._suspend_status = 0
        self._module_status = 0
        self._mode = 0
        self._detect_status = 0
        self._electric_status = 0
        self._dnd_state = 0
        self._warning_breakdown = 0
        self._warning_water_missing = 0
        self._warning_filter = 0
        self._pump_runtime = 0
        self._pump_runtime_today = 0
        self._pump_runtime_readable = 0
        self._pump_runtime_today_readable = 0
        self._purified_water = 0
        self._purified_water_today = 0
        self._filter_percentage = 0
        self._running_status = 0
        self._smart_time_on = 0
        self._smart_time_off = 0
        self._led_switch = 0
        self._led_brightness = 0
        self._led_light_time_on = 0
        self._led_light_time_on_readable = "Uninitialized"
        self._led_light_time_off = 0
        self._led_light_time_off_readable = "Uninitialized"
        self._do_not_disturb_switch = 0
        self._do_not_disturb_time_on = 0
        self._do_not_disturb_time_on_readable = "Uninitialized"
        self._do_not_disturb_time_off = 0
        self._do_not_disturb_time_off_readable = "Uninitialized"
        self._is_locked = 0
        self._led_on_byte1 = 0
        self._led_on_byte2 = 0
        self._led_off_byte1 = 0
        self._led_off_byte2 = 0
        self._dnd_on_byte1 = 0
        self._dnd_on_byte2 = 0
        self._dnd_off_byte1 = 0
        self._dnd_off_byte2 = 0

    @property
    def status(self):
        return {
            "battery": self._battery,
            "dnd_state": self._dnd_state,
            "do_not_disturb_switch": self._do_not_disturb_switch,
            "do_not_disturb_time_off_readable": self._do_not_disturb_time_off_readable,
            "do_not_disturb_time_on_readable": self._do_not_disturb_time_on_readable,
            "energy_consumed": self._energy_consumed,
            "filter_percentage": self._filter_percentage,
            "filter_time_left": self._filter_time_left,
            "is_locked": self._is_locked,
            "led_brightness": self._led_brightness,
            "led_light_time_off_readable": self._led_light_time_off_readable,
            "led_light_time_on_readable": self._led_light_time_on_readable,
            "led_switch": self._led_switch,
            "mac_readable": self._mac_readable,
            "mode": self._mode,
            "name_readable": self._name_readable,
            "power_status": self._power_status,
            "pump_runtime_readable": self._pump_runtime_readable,
            "pump_runtime_today_readable": self._pump_runtime_today_readable,
            "purified_water": self._purified_water,
            "purified_water_today": self._purified_water_today,
            "rssi": self._rssi,
            "running_status": self._running_status,
            "smart_time_off": self._smart_time_off,
            "smart_time_on": self._smart_time_on,
            "voltage": self._voltage,
            "warning_breakdown": self._warning_breakdown,
            "warning_filter": self._warning_filter,
            "warning_water_missing": self._warning_water_missing,
        }
                
    @property
    def config(self):
        return {
            "smart_time_on": self._smart_time_on, 
            "smart_time_off": self._smart_time_off, 
            "led_switch": self._led_switch, 
            "led_brightness": self._led_brightness,
            "led_on_byte1": self._led_on_byte1, 
            "led_on_byte2": self._led_on_byte2,
            "led_off_byte1": self._led_off_byte1,
            "led_off_byte2": self._led_off_byte2,
            "do_not_disturb_switch": self._do_not_disturb_switch,                
            "dnd_on_byte1": self._dnd_on_byte1,
            "dnd_on_byte2": self._dnd_on_byte2,
            "dnd_off_byte1": self._dnd_off_byte1,
            "dnd_off_byte2": self._dnd_off_byte2,
            "is_locked": self._is_locked
        }
        
    @property
    def info(self):
        return {

        }

    @status.setter
    def status(self, status_dict):
        for key, value in status_dict.items():
            attribute_name = f'_{key}'
            if hasattr(self, attribute_name):
                setattr(self, attribute_name, value)
            else:
                raise KeyError(f"Invalid device.status key: {key}")

    @config.setter
    def config(self, config_dict):
        for key, value in config_dict.items():
            attribute_name = f'_{key}'
            if hasattr(self, attribute_name):
                setattr(self, attribute_name, value)
            else:
                raise KeyError(f"Invalid device.config key: {key}")

    @info.setter
    def info(self, info_dict):
        for key, value in info_dict.items():
            attribute_name = key
            if hasattr(self, attribute_name):
                setattr(self, attribute_name, value)
            else:
                raise KeyError(f"Invalid device.info key: {key}")
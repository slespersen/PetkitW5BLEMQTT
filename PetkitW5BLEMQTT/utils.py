# PetkitW5BLE/utils.py
import time
import math
import ctypes
from datetime import datetime, timezone

class Utils:
    def __init__(self):
        pass

    @staticmethod
    def build_command(seq: int, cmd: int, type: int, data: list[int]) -> bytearray:
        header = [250, 252, 253] # In hex our headers are: FA FC FD
        end_byte = [251] # In hex the end byte is FB
        length = len(data)
        start_data = 0
        command = header + [cmd, type, seq, length, start_data] + data + end_byte
        return bytearray(command)

    @staticmethod
    def parse_bytearray(byte_array: bytearray):
        # Here, add logic to parse based on expected structure
        return {
            "header": byte_array[:3],
            "cmd": byte_array[3],
            "type": byte_array[4],
            "seq": byte_array[5],
            "data_length": byte_array[6],
            "data_start": byte_array[7],
            "data": byte_array[8:-1],
            "end_byte": byte_array[-1]
        }
        
    @staticmethod
    def remove_non_matching_entries(original_dict, matching_name):
        filtered_dict = {key: value for key, value in original_dict.items() if key == matching_name}
        return filtered_dict

    @staticmethod
    def split_into_bytes(short_value): 
        short = ctypes.c_short(short_value) 
        byte1 = (short.value >> 8) & 0xFF 
        byte2 = short.value & 0xFF 
        return byte1, byte2
    
    #@staticmethod
    #def split_into_bytes(value):
    #    # Ensure the value is a float
    #    if not isinstance(value, (float, int)):
    #        raise TypeError("Value must be an integer or float")
    #    
    #    # Pack the float value into 2 bytes using 'e' format for 16-bit float
    #    byte_data = struct.pack('e', float(value))
    #    
    #    # Split the packed data into two bytes
    #    byte1, byte2 = byte_data[0], byte_data[1]
    #    
    #    return byte1, byte2

    # HEX string functions
    @staticmethod
    def to_ascii(hex_string: str) -> str:
        return ''.join(chr(b) for b in hex_string)

    @staticmethod
    def trim_hex(hex_string: str) -> str:
        return hex_string[6:-2] # Return only the raw data bytes - including type, sequence, lenght and data start@staticmethod
    
    # Byte manipulation
    @staticmethod
    def unsigned_to_byte(value: str):
        return value.to_bytes(1, byteorder='big', signed=False)

    @staticmethod
    def byte_to_integer(byte):
        return byte & 0xFF

    @staticmethod
    def bytes_to_integer(bytes, byteorder='big'):
        return int.from_bytes(bytes, byteorder=byteorder)

    @staticmethod
    def bytes_to_short(bytes, byteorder='big'):
        return int.from_bytes(bytes, byteorder=byteorder, signed=True)

    @staticmethod
    def bytes_to_long(bytes, byteorder='big'):
        return int.from_bytes(bytes, byteorder=byteorder)
        
    @staticmethod
    def bytes_to_unsigned_integers(byte_array):
        return [b for b in byte_array]
        
    @staticmethod
    def combine_byte_arrays(byte_arrays_dict: dict) -> bytearray:
        combined_array = bytearray()
        for byte_array in byte_arrays_dict.values():
            combined_array.extend(byte_array)
        return combined_array
    
    @staticmethod
    def pad_array(data, target_length):
        return [0] * (target_length - len(data)) + data
    
    @staticmethod
    # String functions
    def reverse_integer_and_append_bytes(integer_value):
        # Reverse the integer by converting it to string, reversing, and converting back to int
        reversed_integer = int(str(integer_value)[::-1])
        # Convert the reversed integer to bytes (big-endian)
        reversed_bytes = reversed_integer.to_bytes((reversed_integer.bit_length() + 7) // 8, byteorder='big')
        # Append 1337 in hex to the end
        appended_bytes = reversed_bytes + bytearray.fromhex('1337')
        return appended_bytes
    
    @staticmethod
    def reverse_unsigned_array(array):
        # Ensure input is a list of integers
        if not all(isinstance(x, int) for x in array):
            raise ValueError("All elements in the array must be integers")
        return array[::-1]
    
    @staticmethod
    def replace_last_two_if_zero(array):
        if len(array) >= 2 and array[-1] == 0 and array[-2] == 0:
            array[-2] = 13
            array[-1] = 37
        return array
    
    # Time functions
    @staticmethod
    def get_seconds():
        date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        now = datetime.utcnow().strftime(date_format) + "+0000"
        reference_time = datetime.strptime("2000-01-01T00:00:00.000+0000", date_format)
        current_time = datetime.strptime(now, date_format)
        seconds = int((current_time - reference_time).total_seconds())
        return seconds

    @staticmethod
    def get_seconds_without_timezone():
        date_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        now = datetime.now(timezone.utc).strftime(date_format)
        reference_time = datetime.strptime("2000-01-01T00:00:00.000+0000", date_format)
        current_time = datetime.strptime(now, date_format)
        seconds = int((current_time - reference_time).total_seconds())
        return seconds

    @staticmethod
    def get_timezone_offset():
        offset = datetime.now().astimezone().utcoffset()
        return int(offset.total_seconds() / 3600.0) + 12

    @staticmethod
    def time_in_bytes():
        datetime_object = [0, 0, 0, 0, 0, 13]
        seconds = Utils.get_seconds()
        
        # Might become relevant later
        #if ble_device_type == 4:
        #    seconds = get_seconds_without_timezone()
        #    datetime_object[0] = (get_timezone_offset() & 255)
        
        datetime_object[1] = (seconds >> 24) & 255
        datetime_object[2] = (seconds >> 16) & 255
        datetime_object[3] = (seconds >> 8) & 255
        datetime_object[4] = (seconds) & 255

        return datetime_object

    @staticmethod
    def get_timestamp_days(timestamp):
        return time.strftime("%-d days, %-H hours", time.gmtime(timestamp))
        
    @staticmethod
    def get_timestamp_hours(timestamp):
        return time.strftime("%-H:%-Mh", time.gmtime(timestamp))
    
    @staticmethod
    def minutes_to_timestamp(minutes): 
        hours = minutes // 60 
        minutes = minutes % 60 
        return f"{hours:02d}:{minutes:02d}"
        
    def time_to_minutes(time_str):
        # Split the input string into hours and minutes
        hour, minute = map(int, time_str.split(':'))
        # Calculate the total minutes
        total_minutes = hour * 60 + minute
        return total_minutes

    # Extract data functions
    @staticmethod
    def trim_data(data):
        # Trim away the header and end bytes (fa, fc, fd, fb)
        if data[:3] == b'\xfa\xfc\xfd' and data[-1] == b'\xfb':
            return data[3:-1]
        return data

    @staticmethod
    def extract_device_id(data):
        bytes = data[2:8]  # Extract first 8 bytes for device ID
        device_id = int.from_bytes(bytes, byteorder='big')
        return Utils.bytes_to_unsigned_integers(bytes), device_id

    @staticmethod
    def extract_serial_number(data):
        bytes = data[8:23]  # Extract next 14 bytes for serial number
        serial_number = ''.join(chr(b) for b in bytes)
        return serial_number

    # measureTime - w5record
    @staticmethod
    def calculate_filtered_water_today(alias, pump_runtime, filter_time_left):
        resources = "days" if filter_time_left > 1 else "day"
        time_text = f"{filter_time_left} {resources}"
        print(time_text)

        canculate_wx_energy_for_type = 0
        canculate_wx_energy_for_type2 = 0.0

        canculate_wx_energy_for_type = int(Utils.canculate_wx_energy_for_type(alias, 1, pump_runtime))
        canculate_wx_energy_for_type2 = Utils.canculate_wx_energy_for_type(alias, 2, pump_runtime)

        if canculate_wx_energy_for_type < 0:
            canculate_wx_energy_for_type = 0

        purified_water_text = f"{max(canculate_wx_energy_for_type2, 0.0)}"
        if canculate_wx_energy_for_type > 1:
            purified_water_text += " times"
        else:
            purified_water_text += " time"
        
        return purified_water_text

    # canculateWxEnergyForType
    # device.alias, device.type_code, 
    @staticmethod
    def calculate_energy_usage(alias, pump_runtime_today):
        f = 0
        f2 = 2.0
        f3 = 1.5
    
        if alias == "W5C":
            f = 0.182
        else:
            f = 0.75 * pump_runtime_today
        
        f2 = 3600000
        
        return f / f2    

    # device.alias, device.type_code, 
    @staticmethod
    def calculate_water_purified(alias, pump_runtime_today):
        f = 0
        f2 = 2.0
        f3 = 1.5
    
        if alias == "W5C":
            f2 = 1.0
            f3 = 1.3
        elif alias == "W4X":
            f2 = 1.8
        elif alias == "CTW3":
            f2 = 3.0
          
        f = (f3 * pump_runtime_today) / 60.0
        
        return f / f2
    
    # canculateWxFilterLeftDays
    # if device.mode = 1 (normal)
    # device.filter_percentage, 1, 0
    # if device.mode = 2 (smart)
    # device.filter_percentage, device.smart_time_on, device.smart_time_off
    @staticmethod
    def calculate_remaining_filter_time(filter_percentage, time_on, time_off):
        return math.ceil(((filter_percentage * 30.0) * (time_on + time_off)) / time_on)
    
    @staticmethod
    def calculate_values(mode, filter_percentage, smart_time_on, smart_time_off, alias, pump_runtime_today, pump_runtime):
        time_on = smart_time_on
        time_off = smart_time_off
        
        if mode == 1:
            time_on = 1
            time_off = 0
    
        filter_time_left = Utils.calculate_remaining_filter_time(filter_percentage, time_on, time_off)
        water_purified_today = Utils.calculate_water_purified(alias, pump_runtime_today)
        water_purified = Utils.calculate_water_purified(alias, pump_runtime)
        energy_consumed = format(Utils.calculate_energy_usage(alias, pump_runtime), 'f')
    
        return filter_time_left, water_purified, water_purified_today, energy_consumed
    
    @staticmethod
    def get_device_properties(device_integer_identifier):
        device_mapping = {
            205: {"name": "Petkit_W5C", "alias": "W5C", "product_name": "Eversweet Mini", "device_type": 14, "type_code": 2},
            206: {"name": "Petkit_W5", "alias": "W5", "product_name": "Eversweet Mini", "device_type": 14, "type_code": 1},
            213: {"name": "Petkit_W5N", "alias": "W5N", "product_name": "Eversweet Mini", "device_type": 14, "type_code": 3},
            214: {"name": "Petkit_W4X", "alias": "W4X", "product_name": "Eversweet 3 Pro", "device_type": 14, "type_code": 4},
            217: {"name": "Petkit_CTW2", "alias": "CTW2", "product_name": "Eversweet Solo 2", "device_type": 14, "type_code": 5},
            223: {"name": "Petkit_CTW3", "alias": "CTW3", "product_name": "Eversweet Max", "device_type": 24, "type_code": 0},
            228: {"name": "Petkit_W4XUVC", "alias": "W4X", "product_name": "Eversweet 3 Pro (UVC)", "device_type": 14, "type_code": 6}
        }

        return device_mapping[device_integer_identifier]
        
    @staticmethod
    def decimal_to_time(decimal_time):
        # Extract the integer part (hours) and the decimal part
        hours = int(decimal_time)
        decimal_minutes = decimal_time - hours

        # Convert the decimal part to minutes (out of 60)
        minutes = int(decimal_minutes * 60)

        return f"{hours:02d}:{minutes:02d}"

# PetkitW5BLEMQTT

Effortlessly connect, control, and monitor your Petkit W5 series water fountains with this no-cloud Python library. Utilizing BLE and MQTT Discovery, integrate your Petkit devices seamlessly with Home Assistant and enjoy total control and insight into your fountains. Your pets will love you for it!

## Features

- **Control Modes:** Switch between Normal and Smart operating modes.
- **Do Not Disturb:** Manage the Do Not Disturb functionality.
- **Filter Management:** Reset the filter and monitor its lifetime.
- **Smart Mode Timings:** Configure both on and off timings for Smart Mode.
- **LED Settings:** Adjust LED intensity and on/off hours.
- **Energy Consumption:** Track energy usage.
- **Warnings:** Receive alerts for breakdowns, filter status, and missing water.
- **Purified Water Monitoring:** Keep tabs on total and daily purified water levels.
- **Voltage & RSSI:** Monitor voltage and signal strength.

## Installation

To install the library, clone the repository and create a symbolic link to your Python library directory:

```sh
git clone https://github.com/slespersen/PetkitW5BLEMQTT.git
ln -s $(pwd)/PetkitW5BLEMQTT /path/to/your/python/site-packages/PetkitW5BLEMQTT
```

### Usage
`supervisor.py` is provided for spawning multiple instances of main.py, in order to handle multiple fountains. Please note that only --mqtt and any mqtt related argument should be passed. The supervisor will find all available instances.

`main.py` is provided for running the library. Below are the arguments it accepts:

### Arguments

- `--address`: (Required) The BLE device address.
- `--mqtt`: (Optional) Enable MQTT.
- `--mqtt_broker`: (Optional) The MQTT broker address.
- `--mqtt_port`: (Optional) The MQTT broker port.
- `--mqtt_user`: (Optional) The MQTT username.
- `--mqtt_password`: (Optional) The MQTT password.
- `--logging_level`: (Optional) The logging level. Default is "INFO".

### Example

Here’s a quick example to get you started:

sh

```
python main.py --address "A1:B2:C3:D4:E5:F6" --mqtt --mqtt_broker "broker.example.com" --mqtt_port 1883 --mqtt_user "user" --mqtt_password "password" --logging_level "INFO"
```

## Caveats

-   Device ID and secret have not been fixed.
    
-   Using the library, especially CMD 73, will set a secret that may interfere with the app's communication with the device.

-	The library currently does not support scheduling Do Not Disturb and Lights Out.
    

## Inspiration, Resources & Acknowledgements

-   [RobertD502](https://github.com/RobertD502): [Home Assistant Petkit Custom Integration](https://www.reddit.com/r/homeassistant/comments/145ebp1/petkit_custom_integration/)
    
-   [RobertD502](https://github.com/RobertD502): [petkitaio](https://github.com/RobertD502/petkitaio)
    
-   [PetKit Eversweet Pro 3 - Decoding BLE response](https://colab.research.google.com/drive/1gWwLz1Wi_WujvvSaTJpPMW5i3YideSAb#scrollTo=RWO3w4-XTmNd)

## Tested Devices

-   **Petkit Eversweet 2 Solo:** This library has been tested and verified to work with the Petkit Eversweet 2 Solo.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.
Should you want to help out, in reverse engineering the secret - please reach out. As I only have two keys, more examples are needed to figure out how the algorithm works.

## Support

For any questions or issues, please open an issue.

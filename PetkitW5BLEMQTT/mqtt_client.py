import paho.mqtt.client as mqtt
import json
import asyncio

class MQTTClient:
    def __init__(self, logger, client_id, broker, port, username=None, password=None, keepalive=60):
    
        try:
            self.client = mqtt.Client(
                client_id=client_id,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION1
            )
        except AttributeError:
            self.client = mqtt.Client(client_id=client_id)

        if username and password:
            self.client.username_pw_set(username, password)
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        self.logger = logger
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_publish = self.on_publish
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        self.logger.info(f"Connected to MQTT broker")
        
    def on_disconnect(self, client, userdata, rc):
        self.logger.info(f"Disconnected from MQTT broker")
        self.connected = False
        
    def on_message(self, client, userdata, msg):
        self.logger.info(f"Message received: {msg.topic} {msg.payload}")

    def set_on_message(self, on_message):
        loop = asyncio.get_running_loop()
        self.client.on_message = lambda client, userdata, message: asyncio.run_coroutine_threadsafe(on_message(client, userdata, message), loop)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.logger.info(f"Subscribed with QoS: {granted_qos}")

    def on_publish(self, client, userdata, mid):
        self.logger.info(f"Message published: {mid}")

    def connect(self):
        self.client.connect(self.broker, self.port, self.keepalive)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def subscribe(self, topic, qos=0):
        self.client.subscribe(topic, qos)

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)

    def publish_availability(self, identifier, state):
        self.client.publish(f"PetkitMQTT/{identifier}/availability", state, 0, True)
        
    def publish_state(self, identifier, state):
        self.client.publish(f"PetkitMQTT/{identifier}/state", json.dumps(state))

    def publish_discovery(self, discovery_payload):
        if isinstance(discovery_payload, list):
            for element in discovery_payload:
                self.client.publish(element["config_topic"], json.dumps(element), retain=True)
        else:
            self.client.publish(f'homeassistant/{discovery_payload["device_class"]}/{discovery_payload["unique_id"]}/config', json.dumps(discovery_payload), retain=True)
        self.connected = True

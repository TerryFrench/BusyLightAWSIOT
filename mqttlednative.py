'''
What is sent: 
{
  "command": "",
  "red": 255,
  "green": 0,  
  "blue": 0,
  "brightness": 0.15
}
 
 command: one of "Black" "Red" "Green" "Blue" "Rainbow"
 
 '''

# from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
# import logging
# import time
# import json
# import blinkt

import json
import logging
import time

import blinkt
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# if set to false, the lights will stay on when the program exits
# blinkt.set_clear_on_exit(False)

# Get broker and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("secrets are kept in secrets.py, please add them there!")
    raise

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    
    # need to process the payload to get what I want/need. 
    # so not the whole string
    doc = json.loads(message.payload)
    command = ""
    try:
        command = doc["command"]
        red = doc["red"]
        green = doc["green"]
        blue = doc["blue"]
        brightness = doc["brightness"]
        blinkt.set_all(red, green, blue, brightness)
    except (ValueError, RuntimeError, KeyError) as e:
        print("Failed to parse values from MQTT message\n", e)
        
    
    # specific commands
    if command == "Green" :
        blinkt.set_all(0, 255, 0, 0.2)
        blinkt.show()
    if command == "Blue" :
        blinkt.set_all(0, 0, 255, 0.2)
        blinkt.show()
    if command == "Red" :
        blinkt.set_all(255, 0, 0, 0.2)
        blinkt.show()
    if command == "Black" :
        blinkt.set_all(0, 0, 0, 0.0)
        blinkt.show()
    if command == "Off" :
        blinkt.set_all(0, 0, 0, 0.0)
        blinkt.show()
    if command == "Rainbow" :
        blinkt.set_pixel(0, 255, 0, 0) #red
        blinkt.set_pixel(1, 255, 127, 0) # orange
        blinkt.set_pixel(2, 255, 255, 0) #yellow
        blinkt.set_pixel(3, 0, 255, 0) #green
        blinkt.set_pixel(4, 0, 255, 127) #cyan
        blinkt.set_pixel(5, 0, 127, 255) # blue cyan
        blinkt.set_pixel(6, 0, 0, 255) # blue 
        blinkt.set_pixel(7, 127, 0, 255) # blue magenta (violet?) 
        blinkt.show()
    
    blinkt.show()
    

host = secrets["broker"]
rootCAPath = secrets["root_ca_path"]
certificatePath = secrets["certificate_path"]
privateKeyPath = secrets["private_key_path"]
clientId = secrets["client_id"]
topic = secrets["topic"]

print("endpoint", host)

port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureEndpoint(host, port)
myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

while True:
    time.sleep(10)

'''
    Command-Line python script to publish some MQTT messages that will set the 8 LED lights
    of a Pimonori Blinkt LED light bar on a Raspberry Pi Zero W that subscribes to the same
    MQTT topic
    
    The clientsecrets.py file contains the secrets. Sample here for the us-east-1 region of AWS
    assuming a "BusyLight" topic on the broker.
    The certificates are generated, activated and downwloaded from the AWS IOT console and should
    be in the same directory as the script 
    Be sure to create the right 
    
    secrets = {
    'broker' : 'XYZ.iot.us-east-1.amazonaws.com',
    'client_id' : 'SOME_CLIENT_NAME',
    'root_ca_path' : 'AmazonRootCA1.pem',
    'certificate_path' : 'YOURCERT.certificate.pem.crt',
    'private_key_path' : 'YOURCERT.private.pem.key',
    'topic' : 'BusyLight'
}

What is sent as the message: 

{
  "command": "",
  "red": 255,
  "green": 0,  
  "blue": 0,
  "brightness": 0.15
}
 
 command: one of "Black" "Off" "Red" "Yellow" "Green" "Blue" "Rainbow"

 '''

# import json
# import argparse
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
from uuid import uuid4

import logging
import time
import argparse
import json

# Get broker and more from a secrets.py file
try:
    from clientsecrets import secrets
except ImportError:
    print("secrets are kept in clientsecrets.py, please add them there!")
    raise

# Nothing means ignore the command
AllowedCommands = ['Black', 'Off', 'Red', 'Yellow', 'Green', 'Blue', 'Rainbow', 'Nothing']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


# Read in command-line parameters
parser = argparse.ArgumentParser()

parser.add_argument("-c", "--command", action="store", dest="command", default="Nothing",
                    help="Operation modes: %s"%str(AllowedCommands))
parser.add_argument("-r", "--red", action="store", dest="red", default=0,
                    help="Red value from 0 to 255", type=int)
parser.add_argument("-g", "--green", action="store", dest="green", default=0,
                    help="Green value from 0 to 255", type=int)
parser.add_argument("-b", "--blue", action="store", dest="blue", default=0,
                    help="Blue value from 0 to 255", type=int)
parser.add_argument("-br", "--brightness", action="store", dest="brightness", default=0.2,
                    help="Brightness value from 0.0 to 1.0", type=float)

args = parser.parse_args()

host = secrets["broker"]
rootCAPath = secrets["root_ca_path"]
certificatePath = secrets["certificate_path"]
privateKeyPath = secrets["private_key_path"]
useWebsocket = False
clientId = secrets["client_id"]
topic = secrets["topic"]

print("endpoint", host)

if args.command not in AllowedCommands:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.command, str(AllowedCommands)))
    exit(2)

# Port defaults
port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.WARNING)
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

# Connect to AWS IoT
myAWSIoTMQTTClient.connect()

#prepare and send the message
message = {}
message['command'] = args.command
message['red'] = args.red
message['green'] = args.green
message['blue'] = args.blue
message['brightness'] = args.brightness
messageJson = json.dumps(message)
myAWSIoTMQTTClient.publish(topic, messageJson, 1)
print('Published topic %s: %s\n' % (topic, messageJson))

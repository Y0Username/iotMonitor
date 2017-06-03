import sys
import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

def pubsub(payload):
	# Feed in parameters
	useWebsocket = False
	host = "a38n5qxkqlw59k.iot.us-west-2.amazonaws.com"
	rootCAPath = "root-CA.crt"
	certificatePath = "iotpi.cert.pem"
	privateKeyPath = "iotpi.private.key"

	# Init AWSIoTMQTTClient
	myAWSIoTMQTTClient = None
	if useWebsocket:
			myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
			myAWSIoTMQTTClient.configureEndpoint(host, 443)
			myAWSIoTMQTTClient.configureCredentials(rootCAPath)
	else:
			myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
			myAWSIoTMQTTClient.configureEndpoint(host, 8883)
			myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

	# AWSIoTMQTTClient connection configuration
	myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
	myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
	myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
	myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
	myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

	# Connect to AWS IoT
	myAWSIoTMQTTClient.connect()
	time.sleep(2)

	# Publish 
	myAWSIoTMQTTClient.publish("sdk/test/Python", json.dumps(payload), 1)
	time.sleep(1)
	
	# Close connection 
	myAWSIoTMQTTClient.connect()


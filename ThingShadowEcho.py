'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from datetime import datetime
import logging
import time
import json
import argparse


class shadowCallbackContainer:
    def __init__(self, deviceShadowInstance):
        self.deviceShadowInstance = deviceShadowInstance

    # Custom Shadow callback
    def customShadowCallback_Delta(self, payload, responseStatus, token):
        # payload is a JSON string ready to be parsed using json.loads(...)
        # in both Py2.x and Py3.x
        print("Received a delta message:")
        payloadDict = json.loads(payload)
        deltaMessage = json.dumps(payloadDict["state"])
        print(deltaMessage)
        print("Request to update the reported state...")
        newPayload = '{"state":{"reported":' + deltaMessage + '}}'
        self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)
        
        print("Sent.")

class mqttConnector:

    def __init__(self):
        self.myAWSIoTMQTTShadowClient = None
        self.deviceShadowHandler = None

    def connect_websocket(self, host, port, rootCAPath, thingName, clientId):
        self.myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
        self.myAWSIoTMQTTShadowClient.configureEndpoint(host, port)
        self.myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
        self.basic_connect(thingName)

    def connect_w_certificates(self, host, port, rootCAPath, privateKeyPath, certificatePath, thingName, clientId):
        self.myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
        self.myAWSIoTMQTTShadowClient.configureEndpoint(host, port)
        self.myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
        self.basic_connect(thingName)

    def basic_connect(self, thingName):
        # AWSIoTMQTTShadowClient configuration
        self.myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
        self.myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

        # Connect to AWS IoT
        self.myAWSIoTMQTTShadowClient.connect()

        # Create a deviceShadow with persistent subscription
        self.deviceShadowHandler = self.myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)
        shadowCallbackContainer_Bot = shadowCallbackContainer(self.deviceShadowHandler)

        # Listen on deltas
        self.deviceShadowHandler.shadowRegisterDeltaCallback(shadowCallbackContainer_Bot.customShadowCallback_Delta)

    def fetchData(self):
        #var readout = dht.read(); 
        #var temp = readout.temperature.toFixed(2); 
        #var humd = readout.humidity.toFixed(2); 
        temp=19
        humd=30
        return '{ "temp": %d, "humd": %d }' %(temp, humd) 
    
    def send_update_temperature(self, newTemperature, newHumidity):
        #newPayload = '{"state":{"reported": %d , "reported_humidity": %d }}' %(newTemperature, newHumidity)
        newPayload = '{"state":{"reported": '+ self.fetchData() + '}}'
        self.deviceShadowHandler.shadowUpdate(newPayload, None, 5)

def main():
    
    # Read in command-line parameters
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
    parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                        help="Use MQTT over WebSocket")
    parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="ThingShadowEcho",
                        help="Targeted client id")

    args = parser.parse_args()
    host = args.host
    rootCAPath = args.rootCAPath
    certificatePath = args.certificatePath
    privateKeyPath = args.privateKeyPath
    port = args.port
    useWebsocket = args.useWebsocket
    thingName = args.thingName
    clientId = args.clientId + str(datetime.now())

    if args.useWebsocket and args.certificatePath and args.privateKeyPath:
        parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
        exit(2)

    if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
        parser.error("Missing credentials for authentication.")
        exit(2)

    # Port defaults
    if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
        port = 443
    if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
        port = 8883

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    
    mqttConnectorInstance = mqttConnector()
    if useWebsocket:
        mqttConnectorInstance.connect_websocket(host, port, rootCAPath, thingName, clientId)
    else:
        mqttConnectorInstance.connect_w_certificates(host, port, rootCAPath, privateKeyPath, certificatePath, thingName, clientId)
        


    # Loop forever
    while True:
        mqttConnectorInstance.send_update_temperature(19, 30)
        time.sleep(1)

if __name__ == '__main__':
    main()



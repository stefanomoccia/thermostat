# -*- coding: utf-8 -*-

from time import sleep
import sys
import random
import cloud4rpi
import rpi
import logging
import threading

class Cloud4RpiConnector():
    # Put your device token here. To get the token,
    # sign up at https://cloud4rpi.io and create a device.
    DEVICE_TOKEN = '6TSQpsPqMQnvuGtzpJuqiobay'
    DATA_SENDING_INTERVAL = 30  # secs
    DIAG_SENDING_INTERVAL = 60  # secs
    POLL_INTERVAL = 0.5  # 500 ms

    def __init__(self, logger, temp_func_callback):
        self.logger = logger
        self.temp_func_callback = temp_func_callback
    
    def run_background(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
    def run(self):
        
        # Put variable declarations here
        # Available types: 'bool', 'numeric', 'string'
        variables = {
            'Room Temp': {
                'type': 'numeric',
                'bind': self.temp_func_callback
            },
            'CPU Temp': {
                'type': 'numeric',
                'bind': rpi.cpu_temp
            },
            #'STATUS': {
            #    'type': 'string',
            #    'bind': listen_for_events
            #}
        }
        diagnostics = {
            'CPU Temp': rpi.cpu_temp,
            'IP Address': rpi.ip_address,
            'Host': rpi.host_name,
            'Operating System': rpi.os_name
        }
        device = cloud4rpi.connect(Cloud4RpiConnector.DEVICE_TOKEN)

        # Use the following 'device' declaration
        # to enable the MQTT traffic encryption (TLS).
        #
        # tls = {
        #     'ca_certs': '/etc/ssl/certs/ca-certificates.crt'
        # }
        # device = cloud4rpi.connect(DEVICE_TOKEN, tls_config=tls)

        try:
            device.declare(variables)
            device.declare_diag(diagnostics)

            device.publish_config()

            # Adds a 1 second delay to ensure device variables are created
            sleep(1)

            data_timer = 0
            diag_timer = 0

            while True:
                if data_timer <= 0:
                    device.publish_data()
                    data_timer = Cloud4RpiConnector.DATA_SENDING_INTERVAL

                if diag_timer <= 0:
                    device.publish_diag()
                    diag_timer = Cloud4RpiConnector.DIAG_SENDING_INTERVAL

                sleep(Cloud4RpiConnector.POLL_INTERVAL)
                diag_timer -= Cloud4RpiConnector.POLL_INTERVAL
                data_timer -= Cloud4RpiConnector.POLL_INTERVAL
            
        except KeyboardInterrupt:
            cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

        except Exception as e:
            error = cloud4rpi.get_error_message(e)
            cloud4rpi.log.exception("ERROR! %s %s", error, sys.exc_info()[0])

        finally:
            sys.exit(0)

# Handler for the button or switch variable
def myValue(self, value=None):
    return 16

#def listen_for_events(self):
    #    # Write your own logic here
    #    result = random.randint(1, 5)
    #    if result == 1:
    #        return 'RING'

    #    if result == 5:
    #        return 'BOOM!'

    #    return 'IDLE'

def main():
    # create logger
    logger = logging.getLogger('cloud4rpi_controller')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    crpi = Cloud4RpiConnector(logger, myValue)
    crpi.run()


if __name__ == '__main__':
    main()

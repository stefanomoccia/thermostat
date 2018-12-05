from telegram_control import TelegramController
from ambient_control import AmbientController
import time
import logging
import threading
from cloud4rpi_connector import Cloud4RpiConnector
from time import sleep

def main():
    
    
    # create logger
    logger = logging.getLogger('thermostat')
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
    
    ambient_control = AmbientController(logger)

    telegram_ctrl = TelegramController(logger, ambient_control.get_ambient_value_message)
    
    
    crpi = Cloud4RpiConnector(logger, ambient_control.get_temperature)
    
    crpi.run_background()
    ambient_control.run_background()

    while True:
            sleep(10)

    
if __name__ == '__main__':
    main()

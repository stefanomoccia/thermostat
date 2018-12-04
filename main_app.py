from telegram_control import TelegramController
from temperature_control import GoogleCalendar
import time
import logging

def main():
    
    
    # create logger
    logger = logging.getLogger('google_thermostat')
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


    telegram_ctrl = TelegramController(logger)
    
    gc = GoogleCalendar(logger)
    gc.calendar_event_check()

    while 1:
        time.sleep(10)

if __name__ == '__main__':
    main()

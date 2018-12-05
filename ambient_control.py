import logging
import threading
from dht11 import DHT11
from google_calendar_connector import GoogleCalendar
from google_calendar_connector import GoogleEvent
from cloud4rpi_connector import Cloud4RpiConnector
from time import sleep
import random

class AmbientValue():
    INVALID_HUMIDITY = 255
    INVALID_TEMPERATURE = 255

    def __init__(self, humidity = INVALID_HUMIDITY, temperature = INVALID_TEMPERATURE, heatingOn = False):
        self.humidity = humidity
        self.temperature = temperature
        self.heatingOn = heatingOn

class AmbientController():
    
    def __init__(self, logger):
        self.logger = logger
        self.dht = DHT11(4)
        self.last_ambient_value = AmbientValue()
        self.last_heating_on = False
        
    
    def read_measure(self):
        result = self.dht.read()
        if result:
            humidity, temperature = result
            return AmbientValue(humidity, temperature)
        else:
            return AmbientValue()

    def get_temperature(self):
        return self.last_ambient_value.temperature

    def get_ambient_value_message(self):
        if (self.last_ambient_value.heatingOn):
            return str("humidity: %s %%,  Temperature: %s C`, Heating: ON" % (self.last_ambient_value.humidity, self.last_ambient_value.temperature))
        else:
            return str("humidity: %s %%,  Temperature: %s C`, Heating: OFF" % (self.last_ambient_value.humidity, self.last_ambient_value.temperature))


    ## Calling this function will automatically:
    #   - read the temperature and humidity from DHT11
    #   - get from the GoogleCalendar the Current Active Event
    #   - calls the parse of the temperature
    #   - checks the target temperature and the actual one and decides to turn on or off heating (logs only as of now)
    def auto_control(self):
        av = self.read_measure()
        self.logger.debug("MEASURED HUMIDITY : %d", av.humidity)
        self.logger.debug("MEASURED TEMPERATURE : %d", av.temperature)

        if (av.humidity != AmbientValue.INVALID_HUMIDITY and av.temperature != AmbientValue.INVALID_TEMPERATURE):
            gc = GoogleCalendar(self.logger)
            ge = gc.get_current_event()
            if(ge.valid):
                target_temp = ge.parse_temperature_event()
                self.logger.debug("CURRENT TARGET TEMPERATURE: %d", target_temp)
                if(target_temp != GoogleEvent.INVALID_TEMPERATURE):
                    if(av.temperature != AmbientValue.INVALID_TEMPERATURE and av.temperature < target_temp):
                        self.logger.error("#####  TURN ON HEATING !! #####")
                        self.last_heating_on = True
                    else:
                        self.logger.error("#####  TURN OFF HEATING !! #####")
                        self.last_heating_on = False
                else:
                    self.logger.error("#####  INVALID CURRENT EVENT FOUND !! #####")
        self.last_ambient_value = AmbientValue(av.temperature, av.humidity, self.last_heating_on)

    def run(self):
        while True:
            self.auto_control()
            sleep(10)

    def run_background(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution
    

def main():
    
    # create logger
    logger = logging.getLogger('ambient_controller')
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

    ac = AmbientController(logger)

    crpi = Cloud4RpiConnector(logger, ac.get_temperature)
    crpi.run_background()
    
    ac.run()
    

    
if __name__ == '__main__':
    main()
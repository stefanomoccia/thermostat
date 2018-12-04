import logging
from dht11 import DHT11
from google_calendar_connector import GoogleCalendar
from google_calendar_connector import GoogleEvent

class AmbientValue():
    INVALID_HUMIDITY = 255
    INVALID_TEMPERATURE = 255

    def __init__(self, humidity = INVALID_HUMIDITY, temperature = INVALID_TEMPERATURE):
        self.humidity = humidity
        self.temperature = temperature

class AmbientController():
    
    def __init__(self, logger):
        self.logger = logger
        self.dht = DHT11(4)
    
    def read_measure(self):
        result = self.dht.read()
        if result:
            humidity, temperature = result
            return AmbientValue(humidity, temperature)
        else:
            return AmbientValue()

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
                    else:
                        self.logger.error("#####  TURN OFF HEATING !! #####")
                else:
                    self.logger.error("#####  INVALID CURRENT EVENT FOUND !! #####")

        
    


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
    ac.auto_control()

    
if __name__ == '__main__':
    main()
from __future__ import print_function
import datetime
import time
import pytz
import logging
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from dateutil import parser

class GoogleEvent():
    INVALID_TEMPERATURE = 255
    
    def __init__(self, valid, summary, startdt, enddt):
        self.valid = valid
        self.summary = summary
        self.startdt = startdt
        self.enddt = enddt
    
    def parse_int(self, s, base=10, val=INVALID_TEMPERATURE):
        if s.isdigit():
            return int(s, base)
        else:
            return val
        
    def parse_temperature_event(self):
        return self.parse_int(self.summary)


class GoogleCalendar():
    #For support and help on API:
    #https://developers.google.com/calendar/v3/reference/calendarList/list?apix_params=%7B%7D

    # If modifying these scopes, delete the file token.json.
    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'

    def __init__(self, logger):
        self.logger = logger

    def calendar_event_check(self):
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next event on the user's calendar.
        """
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('calendar', 'v3', http=creds.authorize(Http()))

        # Call the Calendar API
        calendar_id='091n52epd27p891dj35fk875og@group.calendar.google.com'
        #now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming event from calendar \'Termostat\'')
        #events_result = service.events().list(calendarId='091n52epd27p891dj35fk875og@group.calendar.google.com', timeMin=now,
        #                                    maxResults=1, singleEvents=True,
        #                                    orderBy='startTime').execute()
        #events = events_result.get('items', [])

        

        # get current time
        #ts = time.time()
        # format as a string to be printed
        #start_date = datetime.datetime.fromtimestamp(ts).isoformat() + 'Z'
        #end_date = datetime.datetime.fromtimestamp(ts).isoformat() + 'Z'
        
        #start_date = datetime.datetime(
        #    2017, 10, 30, 00, 00, 00, 0).isoformat() + 'Z'
        #end_date = datetime.datetime(2017, 12, 01, 23, 59, 59, 0).isoformat() + 'Z'
    
        ts = time.time()
        #tz = pytz.timezone('Europe/Rome')
        tz = pytz.UTC
        current_date_time = datetime.datetime.fromtimestamp(ts, tz)
        
        current_date = current_date_time.date()
        today = datetime.datetime.combine(current_date, datetime.time())
        tomorrow = (today + datetime.timedelta(days=1))
        
        start_date = today.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date = tomorrow.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        
        self.logger.debug('############# GOOGLE QUERY #############') 
        self.logger.debug('calendar :' + calendar_id)
        self.logger.debug('TIME MIN:' + start_date)
        self.logger.debug('TIME MAX:' + end_date)


        events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_date,
                timeMax=end_date,
                #maxResults = 1,
                singleEvents=True,
                orderBy='startTime').execute()
        events = events_result.get('items', [])

        self.logger.debug('############# EVENTS LIST #############')
        if not events:
            self.logger.warning('No upcoming events found.')
        
        self.current_event_found = False
        # Create a dummy datetime
        datetimeDummy = datetime.datetime(1900,1,1,0,0,0,0)
        self.current_event = GoogleEvent(False, "dummy", datetimeDummy, datetimeDummy)

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            dt_start = parser.parse(start)
            dt_end = parser.parse(end)
            
            log_msg = ('EVENT:' + event['summary'] + ' START DT: ' + start + ' END DT: ' + end)
            
            if dt_start <= current_date_time <= dt_end:
                self.logger.info("===========> ACTIVE EVENT!! <=========== " + log_msg)
                self.current_event = GoogleEvent(True, event['summary'], dt_start, dt_end)
            else:
                self.logger.debug(log_msg)
        

    def get_current_event(self):
        self.calendar_event_check()
        return self.current_event

def main():
    
    # create logger
    logger = logging.getLogger('google_calendar_connector')
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

    gc = GoogleCalendar(logger)
    gc.calendar_event_check()

    ge = gc.get_current_event()
    logger.info("SUMMARY: " + ge.summary)
    logger.info("STARTDT: " + ge.startdt.strftime('%Y-%m-%dT%H:%M:%SZ'))
    logger.info("ENDDT: " + ge.enddt.strftime('%Y-%m-%dT%H:%M:%SZ'))

if __name__ == '__main__':
    main()
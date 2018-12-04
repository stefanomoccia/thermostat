
import random
import datetime
import telepot
from telepot.loop import MessageLoop
import os

import picamera
import urllib 
import logging

url = 'http://myexternalip.com/raw' 
myip = urllib.urlopen(url).read()

"""
After **inserting token** in the source code, run it:
```
$ python2.7 diceyclock.py
```
"""

class TelegramController:

    def __init__(self, logger):
        self.logger = logger
        self.bot = telepot.Bot('535151350:AAEJqANOJn-FYp5LnSfvd_TDdwyP_5pkfGE')
        MessageLoop(self.bot, self.handle).run_as_thread()

    def handle(self, msg):
        chat_id = msg['chat']['id']
        command = msg['text']

        self.logger.debug('TELEGRAM ## Got command: ' + command)

        if command == '/reboot':
            self.bot.sendMessage(chat_id, str("REBOOTING"))
            os.system("sudo reboot")
        elif command == '/time':
            self.bot.sendMessage(chat_id, str(datetime.datetime.now()))
        elif command == '/ip':
            self.bot.sendMessage(chat_id, str(myip))
        elif command == '/wifion':
            os.system("service hostapd start")
            self.bot.sendMessage(chat_id, str("DONE"))
        elif command == '/wifioff':
            os.system("service hostapd stop")
            self.bot.sendMessage(chat_id, str("BYE"))
        elif command == '/liveon':
            #os.system("/etc/init.d/picam start &")
            #os.system("service motion start")
            os.system("/home/pi/run_ffserver.sh")
        elif command == '/liveoff':
            #os.system("/etc/init.d/picam stop &")
            #os.system("service motion stop")
            os.system("sudo pkill ffserver")
        elif command == '/picture':
            #Get the photo
            #camera=picamera.PiCamera()
            #camera.start_preview()
            #time.sleep(2)
            #camera.capture('./capture.jpg')
            #camera.close()
            self.bot.sendPhoto(chat_id, photo=open('/var/lib/motion/lastsnap.jpg', 'rb'))
        elif command == '/export':
            self.bot.sendPhoto(chat_id, photo=open('./image.png', 'rb'))
        elif command == '/temp':
            result = dht.read()
            if result:
                humidity, temperature = result
                self.bot.sendMessage(chat_id, str("humidity: %s %%,  Temperature: %s C`" % (humidity, temperature)))
            else:
                self.bot.sendMessage("Data Error")

def main():
    
    telegram_ctrl = TelegramController()
    
    print 'I am listening ...'
    
    while 1:
        time.sleep(10)

if __name__ == '__main__':
    main()




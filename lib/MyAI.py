import signal
from threading import Thread

import os
import simplejson as json

from apiai import apiai
import serial
from lib.AwsPolly import AwsPolly
from lib.ImageToText import ImageToText
from lib.IndianTTS import IndianTTS
from lib.LiveStream import LiveStream
from lib.services import get_value, get_env_value


class MyAI:

    def __init__(self):
        self.ai = apiai.ApiAI(get_value('API_AI_CLIENT_ACCESS_TOKEN'))
        self.polly = AwsPolly()
        #self.ser = serial.Serial('/dev/ttyACM0', 9600)

    def start_livestream(self):
        live = LiveStream()
        live.start_youtube_live()
        #print(live.get_live_url())

    def stop_livestream(self):
        print('trying to kill live stream')
        os.kill(LiveStream.process.pid, signal.SIGTERM)

    def get_reply(self, text):
        request = self.ai.text_request()
        request.lang = 'en'  # optional, default value equal 'en'
        request.session_id = "143"
        request.query = text
        ans = request.getresponse().read()
        ans = json.loads(ans)
        print(ans)
        try:
            getattr(self, ans['result']['action'])()
        except AttributeError:
            print('Atribute error')
        return ans['result']['fulfillment']['speech']

    def get_reply_as_speech2(self, text):
        ans = self.get_reply(text)
        self.polly.speak(ans)

    def get_reply_as_speech(self, text):
        ans = self.get_reply(text)
        tts = IndianTTS()
        new_ans = tts.google_translate('ml', ans)
        new_ans = new_ans.replace('!', '')
        new_ans = new_ans.replace('?', '')
        tts.speak_malayalam(new_ans)

    def move_front(self):
        if get_env_value('DEVICE') == 'PI':
            from lib.PiControls import PiControls
            pi = PiControls()
            pi.move_forward()
        else:
            print("sorry! you don't have pi")

    def image_to_text(self):
        img2text = ImageToText()
        img2text.speak_both()

    def turn_on_flash(self):
        if get_env_value('DEVICE') == 'PI':
            from lib.PiControls import PiControls
            pi = PiControls()
            pi.flash_white()
        else:
            print("sorry! you don't have pi")

    def turn_off_flash(self):
        if get_env_value('DEVICE') == 'PI':
            from lib.PiControls import PiControls
            pi = PiControls()
            pi.no_flash_white()
            print("sorry! you don't have pi")










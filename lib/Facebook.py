import urllib

import re
from tempfile import gettempdir

import os
import requests
import simplejson as json
import yaml
from apiai import apiai
import speech_recognition as sr
from urllib import request

from boto3 import Session
from pydub import AudioSegment

from lib.AwsPolly import AwsPolly
from lib.FireStorage import FireStorage
from lib.MyAI import MyAI
from lib.PrintColors import PrintColors
from lib.services import get_value
from lib.services import upload_file


class Facebook:

    reply = {
              "recipient": {
                "id": None
              },
              "message": {
                "text": None
              },
            }

    fb_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + get_value('PAGE_ACCESS_TOKEN')
    data = sender = message = None

    def __init__(self):
        self.seq = 0
        self.myai = MyAI()
        self.polly = AwsPolly()
        self.storage = FireStorage()

    def on_message(self, data):
        self.data = data
        self.sender = data['entry'][0]['messaging'][0]['sender']['id']
        self.__seen()
        if 'messaging' in data['entry'][0]:
            if 'message' in data['entry'][0]['messaging'][0]:
                self.message = data['entry'][0]['messaging'][0]['message']
                if self.seq != data['entry'][0]['messaging'][0]['message']['seq']:
                    self.seq = data['entry'][0]['messaging'][0]['message']['seq']
                    if 'text' in data['entry'][0]['messaging'][0]['message']:
                        self.send_reply()
                    elif 'attachments' in data['entry'][0]['messaging'][0]['message']:
                        if data['entry'][0]['messaging'][0]['message']['attachments'][0]['type'] == 'audio':
                            print('attachment audio')
                            self.send_reply_audio()

            else:
                print(PrintColors.OKBLUE + str(data))
        else:
            print(PrintColors.WARNING + str(data))

    def send_reply(self):

        try:
            self.__is_typing(True)
            reply = self.reply.copy()
            reply['recipient']['id'] = self.sender
            reply['message']['text'] = self.myai.get_reply(self.message['text'])
            headers = {'Content-Type': 'application/json'}
            self.__is_typing(False)
            r = requests.post(self.fb_url, headers=headers, data=json.dumps(reply))
            print(PrintColors.OKGREEN + r.text)
            return True
        except Exception as e:
            print(e)

    def __is_typing(self, val):
        message = {
          "recipient": {
            "id": self.sender
          },
          "sender_action": "typing_on" if val else "typing_off"
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.post(self.fb_url, headers=headers, data=json.dumps(message))
        print(PrintColors.OKGREEN + r.text)

    def __seen(self):
        message = {
          "recipient": {
            "id": self.sender
          },
          "sender_action": "mark_seen"
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.post(self.fb_url, headers=headers, data=json.dumps(message))
        print(PrintColors.OKGREEN + r.text)

    def send_reply_audio(self):
        self.__is_typing(True)
        audio_url = self.message['attachments'][0]['payload']['url']
        urllib.request.urlretrieve(audio_url, os.path.join(gettempdir(), "audio.mp4"))
        r = sr.Recognizer()
        mp4_version = AudioSegment.from_file(os.path.join(gettempdir(), "audio.mp4"), "mp4")
        mp4_version.export(os.path.join(gettempdir(), "audio.wav"), format='wav')
        with sr.AudioFile(os.path.join(gettempdir(), "audio.wav")) as source:
            audio = r.record(source)  # read the entire audio file
        try:
            text = r.recognize_google_cloud(audio, credentials_json=open('google-cloud.json').read())
            print("Google Cloud Speech thinks you said " + text)
            ans = self.myai.get_reply(text)
            reply_audio_path = self.polly.get_audio(ans)
        except sr.UnknownValueError:
            print("Google Cloud Speech could not understand audio")
            reply_audio_path = self.polly.get_audio('could not understand audio')
        except sr.RequestError as e:
            print("Could not request results from Google Cloud Speech service; {0}".format(e))
            reply_audio_path = self.polly.get_audio('Could not request results from Google Cloud Speech service')
        print("requesting file upload : " + reply_audio_path)
        reply = self.reply.copy()
        reply['recipient']['id'] = self.sender
        reply['message'] = {
            "attachment": {
              "type": "audio",
              "payload": {
                  'url':  self.storage.upload_fb_audio(reply_audio_path)
              }
            }
          }
        self.__is_typing(False)
        headers = {'Content-Type': 'application/json'}
        r = requests.post(self.fb_url, headers=headers, data=json.dumps(reply))
        print(PrintColors.OKGREEN + r.text)
        return True



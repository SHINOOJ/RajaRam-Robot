

import requests
from html.parser import HTMLParser

from google.oauth2 import service_account

from lib.AwsPolly import AwsPolly
from lib.services import play

from google.cloud import translate

# Instantiates a client

class IndianTTS:
    def google_translate(self, target, text):
        credentials = service_account.Credentials.from_service_account_file(
            '../google-cloud.json')
        translate_client = translate.Client(credentials=credentials)
        # Translates some text into Russian
        translation = translate_client.translate(
            text,
            target_language=target)

        print(u'Text: {}'.format(text))
        print(u'Translation: {}'.format(translation['translatedText']))
        return translation['translatedText']

    def speak_malayalam(self, text):
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {
            'op': text,
            'Languages': 'malayalam',
            'Voice': 'voice1',
            'ip': '',
            'rate': 'normal',
            'ex': 'execute',
        }

        session = requests.Session()
        reply = session.post('http://210.212.237.167/tts/festival_cs.php', headers=headers, data=payload)
        # print(reply.text)
        parser = MyHTMLParser()
        parser.feed(reply.text)


class MyHTMLParser(HTMLParser):


    def handle_starttag(self, tag, attrs):
        print("Start tag:", tag)
        if tag == 'source':
            for attr in attrs:
                if attr[0] == 'src':
                    print("     attr:", attr[1])
                    play('http://210.212.237.167/tts/'+attr[1])





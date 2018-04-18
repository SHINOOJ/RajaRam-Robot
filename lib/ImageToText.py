import io
import types

from cv2 import *
from google.cloud import vision
from google.oauth2 import service_account

from lib.AwsPolly import AwsPolly
from lib.IndianTTS import IndianTTS


class ImageToText:

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            'google-cloud.json')
        self.client = vision.ImageAnnotatorClient(credentials=credentials)

    def capture_image(self):
        cam = VideoCapture(0)  # 0 -> index of camera
        s, img = cam.read()
        imwrite("img2text.jpg", img)  # save image

    def get_text(self):
        self.capture_image()
        with io.open('img2text.jpg', 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = self.client.text_detection(image=image)
        texts = response.text_annotations
        print('Texts:' + texts[0].description)
        return texts[0].description

    def speak_malayalam(self):
        text = self.get_text()
        tts = IndianTTS()
        new_ans = tts.google_translate('ml', text)
        new_ans = new_ans.replace('!', '')
        new_ans = new_ans.replace('?', '')
        tts.speak_malayalam(new_ans)

    def speak_both(self):
        text = self.get_text()
        polly = AwsPolly()
        polly.speak(text=text)
        tts = IndianTTS()
        new_ans = tts.google_translate('ml', text)
        new_ans = new_ans.replace('!', '')
        new_ans = new_ans.replace('?', '')
        tts.speak_malayalam(new_ans)

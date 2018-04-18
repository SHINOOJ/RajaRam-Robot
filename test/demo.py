import io
import types

from cv2 import *
from google.cloud import vision
from google.oauth2 import service_account

cam = VideoCapture(0)   # 0 -> index of camera
s, img = cam.read()
imwrite("img2text.jpg", img) #save image


credentials = service_account.Credentials.from_service_account_file(
        '../google-cloud.json')
client = vision.ImageAnnotatorClient(credentials=credentials)

 # [START migration_text_detection]
with io.open('img2text.jpg', 'rb') as image_file:
    content = image_file.read()

image = vision.types.Image(content=content)

response = client.text_detection(image=image)
texts = response.text_annotations
print('Texts = :' + texts[0].description)





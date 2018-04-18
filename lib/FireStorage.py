from pyrebase import pyrebase

from lib.services import get_value


class FireStorage:

    def __init__(self):
        config = get_value('FIREBASE')
        firebase = pyrebase.initialize_app(config)
        self.storage = firebase.storage()

    def upload_fb_audio(self, file):
        my_file = self.storage.child('facebook').child('audio').child('audio.mp3')
        print('uploading file')
        my_file.put(file=file)
        return 'https://firebasestorage.googleapis.com/v0/b/rajaram-firebase.appspot.com/o/facebook%2Faudio%2Faudio.mp3?alt=media&token=6a837287-1bc9-4463-9657-e3b30ed8472c'
from pyrebase import pyrebase

from lib.services import get_value


class FireDB:

    def __init__(self):
        config = get_value('FIREBASE')
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def set_fb_live(self, url):
        print("updating database")
        url_data = self.db.child('facebook').child('live_stream').child('stream_url')
        url_data.set(url)
        status_data = self.db.child('facebook').child('live_stream').child('status')
        status_data.set('LIVE')

    def set_robot_url(self,url):
        print("updating database with robot url")
        self.db.child('robot').child('url').set(url)
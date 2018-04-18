import threading
from threading import Thread

import lib.Ngrok
from lib import bottle
from lib.MicrophoneStream import MicrophoneStream
from lib.Server import Server
myapp = Server()
bgm_thread = threading.Thread(target=myapp.play_bgm)
ngrok = lib.Ngrok.Ngrok()
threading.Thread(target=myapp.stream_speach).start()
bottle.route("/messenger", method=['POST'])(myapp.messengerFromFirebase)
bottle.route("/appNotification", method=['POST'])(myapp.app_notification)
bottle.run(host='localhost', port=9000)
#time.sleep(10)


import simplejson as json
import platform
import subprocess
import threading
import urllib.request
import time

import yaml

from lib.FireDB import FireDB
from lib.PrintColors import PrintColors
from lib.services import get_value, get_env_value


class Ngrok:

    ngrok_path = {'x86_64': {
        'Linux': './bin/ngrok/ngrok-stable-linux-amd64/ngrok',
        'Windows': './bin/ngrok/ngrok-stable-windows-amd64/ngrok.exe'
        },
        'armv7l': {
            'Linux': './bin/ngrok/ngrok-stable-linux-arm/ngrok'
        }
    }
    tunnel_url = 'http://localhost:4040/api/tunnels'

    def __init__(self):
        self.server_url = get_value('SERVER_URL')
        self.machine = platform.machine()
        self.system = platform.system()
        print('Detected machine : ' + self.machine)
        print('Detected system : ' + self.system)
        threading.Thread(target=self.start_ngrok())
        self.get_public_url()

    def start_ngrok(self):
        print('starting tunnel')
        self.process = subprocess.Popen([self.ngrok_path[self.machine][self.system], "http", "9000"], stdout=subprocess.PIPE)

    def get_public_url(self):
        time.sleep(.2)
        try:
            val = urllib.request.urlopen(self.tunnel_url).read()
            val = json.loads(val)
            if len(val['tunnels']) is 2:
                print('client url obtained')
                self.update_server_url(val['tunnels'][0]['public_url'])
            else:
                #time.sleep(2)
                self.get_public_url()
        except:
            self.get_public_url()

    def update_server_url(self, url):
        print('robot url : '+url)
        fireDB = FireDB()
        fireDB.set_robot_url(url)

    def __del__(self):
        if get_env_value('DEVICE') == 'PI':
            from lib.PiControls import PiControls
            pi = PiControls()
            pi.no_led_flash()
        else:
            print("sorry! can't blink yellow you don't have pi")
        print(PrintColors.WARNING + "killing ngrok")
        self.process.kill()





import re

import os
import wave

import pyaudio
import requests
import sys
import yaml
import subprocess
import speech_recognition as sr


def get_value(key):
    with open('app.yaml') as f:
        # use safe_load instead load
        data_map = yaml.safe_load(f)
        return data_map[key]


def get_env_value(key):
    with open('env.yaml') as f:
        # use safe_load instead load
        data_map = yaml.safe_load(f)
        return data_map[key]


def upload_file(path):
    file = {
        'upload_file': open(path, 'rb')
    }
    url = get_value('SERVER_URL') + '/fileUpload'
    r = requests.post(url, files=file)
    server_url = get_value('SERVER_URL')
    server_url = re.sub('api$', '', server_url)
    final_url = server_url + r.text
    print(final_url)
    return final_url


def play(file_path):
        # Play the audio using the platform's default player
        if sys.platform == "win32":
            os.startfile(file_path)
        else:
            # the following works on Mac and Linux. (Darwin = mac, xdg-open = linux).
            # opener = ["open"] if sys.platform == "darwin" else ["xdg-open"]
            opener = ["open"] if sys.platform == "darwin" else ['vlc', '--intf', 'dummy', '--play-and-exit']
            subprocess.call(opener + [file_path])





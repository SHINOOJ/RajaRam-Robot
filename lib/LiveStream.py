import re
import threading

import simplejson as json
import os
import requests
import sys
import subprocess

import time

from bs4 import BeautifulSoup

from lib.FireDB import FireDB
from lib.PrintColors import PrintColors
from lib.services import get_value, get_env_value


class LiveStream:

    process = None

    def __init__(self):
        self.db = FireDB()
        threading.Thread(self.__start_avconv())

    def start_youtube_live(self):
        print('my youtube')
        LiveStream.process = subprocess.Popen(
            ['avconv', '-f', 'video4linux2', '-r', '10', '-i', '/dev/video0', '-i',
             'resources/bgm.mp3', '-vcodec', 'h264', '-preset', 'medium', '-acodec', 'mp3', '-ar', '44100',
             '-threads', '1', '-qscale', '3', '-b:a', '128k', '-b:v', '500k', '-minrate', '500k', '-g', '60',
             '-pix_fmt', 'yuv420p', '-f', 'flv', 'rtmp://a.rtmp.youtube.com/live2/ekta-g21u-ttm3-985p'], stdout=subprocess.PIPE)

    def __start_avconv(self):
        stream_url = self.__get_stream_url()
        LiveStream.process = subprocess.Popen(['avconv', '-f', 'video4linux2', '-r', '10', '-i', '/dev/video0', '-f', 'pulse', '-ac', '1', '-i', get_env_value('AUDIO_DEVICE'), '-vcodec', 'h264', '-preset', 'medium', '-acodec', 'mp3', '-ar', '44100', '-threads', '1', '-qscale', '3', '-b:a', '128k', '-b:v', '500k', '-minrate', '500k', '-g', '60', '-pix_fmt', 'yuv420p', '-f', 'flv', stream_url], stdout=subprocess.PIPE)

    def __get_stream_url(self):
        url = 'https://graph.facebook.com/v2.6/267660563733964/live_videos?access_token=' + get_value('PAGE_ACCESS_TOKEN')
        r = requests.post(url).json()
        self.stream_data = r
        print(r)
        self.key = re.sub('rtmp://live-api-a.facebook.com:80/rtmp/', '', r['stream_url'])
        print('key ; ' + self.key)
        return r['stream_url']

    def get_live_url(self):
        print(PrintColors.WARNING + 'waiting stream publishing' + PrintColors.WARNING)
        time.sleep(2)
        url = 'https://graph.facebook.com/v2.6/267660563733964'
        param = {
            'fields': 'live_videos',
            'access_token': get_value('PAGE_ACCESS_TOKEN')
        }
        r = requests.get(url, params=param).json()
        for data in r['live_videos']['data']:
            if data['stream_url'] == self.stream_data['stream_url'] and data['status'] == 'LIVE':
                print(data['embed_html'])
                iframe = data['embed_html']
                soup = BeautifulSoup(iframe, "html.parser")
                embed_url = soup.find_all('iframe')[0].get('src')
                self.db.set_fb_live(embed_url)
                return embed_url
            else:
                return self.get_live_url()

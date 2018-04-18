import threading

import boto3
import pygame
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
from lib.services import get_value


class AwsPolly:
    session = boto3.Session()
    polly = session.client("polly")

    def get_audio(self, text):
        try:
            # Request speech synthesis
            response = self.polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Matthew")
        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            print(error)
            sys.exit(-1)

        # Access the audio stream from the response
        if "AudioStream" in response:
            # Note: Closing the stream is important as the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                self.output = os.path.join(gettempdir(), "speech.mp3")

                try:
                    # Open a file for writing the output as a binary stream
                    with open(self.output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)

        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")
        return self.output

    def speak(self, text):
        self.get_audio(text)
        self._play()

    def _play(self):
        # Play the audio using the platform's default player
        if sys.platform == "win32":
            os.startfile(self.output)
        else:
            # the following works on Mac and Linux. (Darwin = mac, xdg-open = linux).
            # opener = ["open"] if sys.platform == "darwin" else ["xdg-open"]
            opener = ["open"] if sys.platform == "darwin" else ['vlc', '--intf', 'dummy', '--play-and-exit']
        subprocess.call(opener + [self.output])

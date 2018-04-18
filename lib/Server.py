import os
import threading
import wave

import pyaudio
import simplejson as json
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.oauth2 import service_account
from pocketsphinx import LiveSpeech,get_model_path
import re
import sys
from lib.AwsPolly import AwsPolly
from lib.Facebook import Facebook
from lib.MicrophoneStream import MicrophoneStream
from lib.MyAI import MyAI
from lib.bottle import request
import speech_recognition as sr

from lib.services import get_env_value

interrupted = False
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class Server:

    def __init__(self):
        self.fb = Facebook()
        self.ai = MyAI()

    def messenger(self):
        message = json.loads(request.json)
        print(message)
        self.fb.on_message(message)
        return message

    def app_notification(self):
        message = json.loads(request.body.read())
        print(message)
        polly = AwsPolly()
        polly.speak(message['tickerText'])
        return {
            "reply": self.ai.get_reply(message['tickerText'])
        }

    def messengerFromFirebase(self):
        message = json.loads(request.body.read())
        print(message)
        self.fb.on_message(message)

    def listen_speech(self):
        # obtain audio from the microphone
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
        # obtain audio from the microphone
        r = sr.Recognizer()
        try:
            with sr.Microphone(device_index=get_env_value('AUDIO_DEVICE_INDEX1')) as source:
                r.adjust_for_ambient_noise(source, duration=1)
                print("Say something!")
                if get_env_value('DEVICE') == 'PI':
                    from lib.PiControls import PiControls
                    pi = PiControls()
                    pi.flash_red()
                else:
                    print("sorry! can't blink red you don't have pi")
                audio = r.listen(source,phrase_time_limit=2)
        except Exception as e:
            print(e)
        if get_env_value('DEVICE') == 'PI':
            from lib.PiControls import PiControls
            pi = PiControls()
            pi.flash_yellow()
        else:
            print("sorry! can't blink yellow you don't have pi")
        print("converting")

        # recognize speech using Google Speech Recognition
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            text = r.recognize_google(audio)
            print("Speech Recognition thinks you said " + text)
            self.ai.get_reply_as_speech(text)
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Speech Recognition service; {0}".format(e))
        if get_env_value('DEVICE') == 'PI':
            from lib.PiControls import PiControls
            pi = PiControls()
            pi.flash_blue()
        else:
            print("sorry! can't blink blue you don't have pi")
        #self.listen_speech()

    def signal_handler(self,signal, frame):
        global interrupted
        interrupted = True

    def interrupt_callback(self):
        global interrupted
        return interrupted


    def pocketsphinix(self):
        model_path = get_model_path()
        speech = LiveSpeech(
            verbose=False,
            sampling_rate=16000,
            buffer_size=2048,
            no_search=False,
            full_utt=False,
            hmm=os.path.join(model_path, 'en-us'),
            lm=os.path.join(model_path, 'en-us.lm.bin'),
            dic=os.path.join(model_path, 'cmudict-en-us.dict')
        )
        for phrase in speech:
            print(phrase)

    def listen_print_loop(self,responses):
        """Iterates through server responses and prints them.
        The responses passed is a generator that will block until a response
        is provided by the server.
        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.
        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r'\b(hello)\b', transcript, re.I):
                    print('hotword detected..')
                    self.listen_speech()
                elif re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    break

                num_chars_printed = 0

    def stream_speach(self):
        try:
            if get_env_value('DEVICE') == 'PI':
                from lib.PiControls import PiControls
                pi = PiControls()
                pi.flash_blue()
            else:
                print("sorry! can't blink blue you don't have pi")

            print('live speech recognition started')
            print(threading.enumerate())
            # See http://g.co/cloud/speech/docs/languages
            # for a list of supported languages..
            language_code = 'en-US'  # a BCP-47 language tag
            credentials = service_account.Credentials.from_service_account_file(
                'google-cloud.json')
            client = speech.SpeechClient(credentials=credentials)
            config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=language_code)
            streaming_config = types.StreamingRecognitionConfig(
                config=config,
                interim_results=True)

            with MicrophoneStream(RATE, CHUNK) as stream:
                audio_generator = stream.generator()
                requests = (types.StreamingRecognizeRequest(audio_content=content)
                            for content in audio_generator)

                responses = client.streaming_recognize(streaming_config, requests)

                # Now, put the transcription responses to use.
                self.listen_print_loop(responses)
        except:
            print('exception occured')
            self.stream_speach()

    def play_bgm(self):
        CHUNK = 1024
        p = pyaudio.PyAudio()
        wf = wave.open('./resources/terminator.wav', 'rb')
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(CHUNK)

        while data != '':
            stream.write(data)
            data = wf.readframes(CHUNK)

        stream.stop_stream()
        stream.close()
        p.terminate()
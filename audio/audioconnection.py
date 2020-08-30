import audioop
import wave
import time
from array import array
from sys import byteorder

import pyaudio

from audio.ring_buffer import RingBuffer


class AudioConnection(object):
    def __init__(self, audio_library):
        self.audio = audio_library
        self.CHUNK = 1024
        self.SILENCE_THRESHOLD = 10  # RMS
        self.SILENCE_TIMEOUT = 1  # seconds
        self.SAMPLE_SIZE = self.audio.get_sample_size(pyaudio.paInt16)
        self.ring_buffer = RingBuffer(self.channels * self.sample_rate * 5)

        self.audio_in = pyaudio.Stream(PA_manager=self.audio,
                                       rate=self.sample_rate,
                                       channels=self.channels,
                                       format=pyaudio.paInt16,
                                       input=True,
                                       output=False,
                                       frames_per_buffer=self.CHUNK,
                                       stream_callback=self.on_audio_in,
                                       start=False)

    @property
    def sample_rate(self):
        return 16000 

    @property
    def channels(self):
        return 1

    def record(self):
        time_passed = 0
        audio_buffer = array('h')
        wait_for_utterance_silence = True

        if not self.audio_in.is_active():
            self.audio_in.start_stream()

        while self.audio_in.is_active():
            chunk = self.fetch_chunk()

            if self.is_silence(chunk) and wait_for_utterance_silence:
                time.sleep(0.2)
                print('.', end='', flush=True)
                continue

            wait_for_utterance_silence = False

            audio_buffer.extend(chunk)
            if self.is_silence(chunk):
                time_passed += len(chunk) / self.sample_rate

                if time_passed > self.SILENCE_TIMEOUT:
                    self.audio_in.stop_stream()
            else:
                time_passed = 0
        print(time_passed)
        return audio_buffer

    def dispose(self):
        """
        Terminates audio stream and releases its resources.
        """
        self.audio_in.close()
        self.audio.terminate()

    def on_audio_in(self, in_data, frame_count, time_info, flag):
        """
        :param in_data: recorded data if input=True; else None
        :param frame_count: number of frames
        :param time_info: dictionary
        :param flag: PaCallbackFlags
        :return:
        """
        self.ring_buffer.extend(in_data)
        return None, pyaudio.paContinue

    def fetch_chunk(self):
        audio_frame = self.ring_buffer.get()
        chunk = array('h', audio_frame)
        if byteorder == 'big':
            chunk.byteswap()
        return chunk

    def is_silence(self, audio):
        power = audioop.rms(audio, self.SAMPLE_SIZE)
        return power < self.SILENCE_THRESHOLD


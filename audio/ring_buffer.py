import collections


class RingBuffer(object):
    def __init__(self, size=4096):
        """
        Ring buffer to hold audio from PortAudio

        :param size:
        """
        self.audio_buffer = collections.deque(maxlen=size)

    def extend(self, data):
        """
        Adds data to the end of buffer

        :param data:
        :return:
        """
        self.audio_buffer.extend(data)

    def get(self):
        """
        Retrieves data from the beginning of buffer and clears it

        :return:
        """
        chunk = bytes(bytearray(self.audio_buffer))
        self.audio_buffer.clear()
        return chunk


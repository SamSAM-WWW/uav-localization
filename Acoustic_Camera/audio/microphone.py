import os
import wave

import pyaudio

from common.consts import RECORDS_PATH, WAV_FILE_NAME
from common.log import debug
from common.process_sync import should_stop

import sounddevice as sd

FRAME_RATE = 16000

SAMPLE_FORMAT = pyaudio.paInt16


class MicArray:
    def __init__(self, output_path=None, rate=FRAME_RATE, chunk_size=None):
        self.pyaudio_instance = None
        self.stream = None
        self.channels = 16
        self.sample_rate = rate
        self.chunk_size = chunk_size if chunk_size else 1024
        os.makedirs(RECORDS_PATH, exist_ok=True)
        self._output_path = output_path if output_path else os.path.join(RECORDS_PATH, WAV_FILE_NAME)
        self.frames = []

    def _select_mic_device_index(self):
        channels = 16
        name_keyword = "UMA16"
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if name_keyword.lower() in dev['name'].lower() and dev['max_input_channels'] >= channels:
                print(f"Found matching device at index {i}: {dev['name']}")
                return i
        raise RuntimeError(f"No input device found with keyword '{name_keyword}'")
    
    def run(self):
        self.frames = []
        self.pyaudio_instance = pyaudio.PyAudio()
        device_index = self._select_mic_device_index()
        self.stream = self.pyaudio_instance.open(
            format=SAMPLE_FORMAT,
            channels=self.channels,
            rate=self.sample_rate,
            frames_per_buffer=self.chunk_size,
            input=True,
            input_device_index=device_index,
        )

        debug('Recording audio, press Ctrl+C to stop recording')

        frames = []  # Initialize array to store frames


        try:
            while True:
                data = self.stream.read(self.chunk_size)
                frames.append(data)
                if should_stop():
                    raise KeyboardInterrupt()
        except KeyboardInterrupt:
            debug('Quitting audio recording')

        # Stop and close the stream
        self.stream.stop_stream()
        self.stream.close()
        # Terminate the PortAudio interface
        self.pyaudio_instance.terminate()

        debug('Finished recording audio')

        # Save the recorded data as a WAV file
        wf = wave.open(self._output_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pyaudio_instance.get_sample_size(SAMPLE_FORMAT))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()


def audio_capture():
    mic = MicArray()
    mic.run()

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write as wavwrite

fs = 48000
channels = 1  # 1 channel
duration = 3.0
device_index = None  # 

print("Recording...")
data = sd.rec(int(fs * duration), samplerate=fs, channels=channels, device=device_index, dtype='float32')
sd.wait()
print("Recording done.")


print("min:", np.min(data), "max:", np.max(data), "mean:", np.mean(data))


wavwrite("test_single_channel.wav", fs, np.int16(data * 32767))
print("Saved test_single_channel.wav")

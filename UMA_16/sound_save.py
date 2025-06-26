import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write as wavwrite
import os
from datetime import datetime

fs = 48000
channels = 16
duration = 5.0  # seconds
target_name = "UMA16"

# Search for input device
def find_input_device(name_keyword):
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if name_keyword.lower() in dev['name'].lower() and dev['max_input_channels'] >= channels:
            print(f"Found matching device at index {i}: {dev['name']}")
            return i
    raise RuntimeError(f"No input device found with keyword '{name_keyword}'")

device_index = find_input_device(target_name)

# Record audio
print("Recording...")
data = sd.rec(int(fs * duration), samplerate=fs, channels=channels,
              device=device_index, dtype='float32')
sd.wait()
print("Done recording.")

#folder and file
output_dir = "recorded_audio"
os.makedirs(output_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{timestamp}.wav"
filepath = os.path.join(output_dir, filename)

# set gain
gain = 5.0  
data = np.clip(data * gain, -1.0, 1.0)  

# Save to WAV file (normalize to int16 if needed)
wav_data = np.int16(data * 32767)
wavwrite(filepath, fs, wav_data)
print(np.min(data), np.max(data), np.mean(data))
print(f"Saved audio file: {filepath}")


import matplotlib.pyplot as plt
plt.plot(data[:1000, 0])  # 第1个通道前1000个点
plt.show()


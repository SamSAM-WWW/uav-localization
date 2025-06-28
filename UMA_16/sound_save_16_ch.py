# 16 channel sound save to 16 files

import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write as wavwrite
import os
from datetime import datetime


# Search for input device
def find_input_device(name_keyword):
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if name_keyword.lower() in dev['name'].lower() and dev['max_input_channels'] >= channels:
            print(f"Found matching device at index {i}: {dev['name']}")
            return i
    raise RuntimeError(f"No input device found with keyword '{name_keyword}'")

if __name__ == '__main__':
    fs = 48000
    channels = 16
    duration = 10.0  # seconds
    target_name = "UMA16"

    device_index = find_input_device(target_name)

    # Record audio
    print("Recording...")
    data = sd.rec(int(fs * duration), samplerate=fs, channels=channels,
                device=device_index, dtype='float32')
    sd.wait()
    print("Done recording.")

    # Gain and clip
    gain = 5.0
    data = np.clip(data * gain, -1.0, 1.0)

    # Create timestamped subfolder inside "recorded_audio"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_output_dir = "recorded_audio"
    session_dir = os.path.join(base_output_dir, timestamp)
    os.makedirs(session_dir, exist_ok=True)

    # Save each channel separately into subfolder
    for ch in range(channels):
        ch_data = data[:, ch]
        wav_data = np.int16(ch_data * 32767)
        filename = f"ch{ch}.wav"
        filepath = os.path.join(session_dir, filename)
        wavwrite(filepath, fs, wav_data)
        print(f"Saved: {filepath}")

    # Optional plot
    plt.figure(figsize=(12, 10))
    for ch in range(channels):
        plt.plot(data[:1000, ch], label=f'ch {ch}')
    plt.title(f"First 1000 samples - Recording {timestamp}")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    plt.show()
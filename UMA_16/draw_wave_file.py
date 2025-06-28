### be careful when running this code. if the audio file is big, it may take a long time and your pc may be no response
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# read .wav file
file_path = "/home/jetson/mycode/uav-localization/Acoustic_Camera/recorder_output/records/audio.wav"
sample_rate, data = wavfile.read(file_path)
print("file found")

print("processing")
duration = data.shape[0] / sample_rate
print("duration = ",duration)
time_axis = np.linspace(0, duration, data.shape[0])

# single / multiple ch
if data.ndim == 1:
    print("single ch")
    # single
    plt.figure(figsize=(12, 4))
    plt.plot(time_axis, data)
    plt.title("Waveform (Mono)")
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.grid(True)
else:
    print("multi ch")
    channels = data.shape[1]
    plt.figure(figsize=(12, channels * 2))
    for i in range(channels):
        plt.subplot(channels, 1, i + 1)
        plt.plot(time_axis, data[:, i])
        plt.title(f"Channel {i}")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        plt.grid(True)

plt.tight_layout()
plt.suptitle("Waveform of .wav File", fontsize=16, y=1.02)
plt.show()
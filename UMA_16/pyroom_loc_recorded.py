import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from pyroomacoustics.doa import SRP
from scipy.signal import stft

# Configuration parameters
wav_path = "Acoustic_Camera//recorder_output//records//audio.wav"
nfft = 512
c = 343.0  # Speed of sound, in m/s
azimuth_grid = np.linspace(0, 360, 360)  # Azimuth search range

# Read multi-channel wav data, shape: (samples, channels)
data, fs = sf.read(wav_path)
print(f"WAV Loaded. Shape: {data.shape}, fs={fs} Hz")

# Transpose to (channels, samples)
data = data.T

# UMA-16 microphone array planar coordinates, unit: meters, shape: (3, 16)
mic_positions = np.array([
    [0.021, -0.063, 0.0], [0.063, -0.063, 0.0],
    [0.021, -0.021, 0.0], [0.063, -0.021, 0.0],
    [0.021,  0.021, 0.0], [0.063,  0.021, 0.0],
    [0.021,  0.063, 0.0], [0.063,  0.063, 0.0],
    [-0.063, 0.063, 0.0], [-0.021, 0.063, 0.0],
    [-0.063, 0.021, 0.0], [-0.021, 0.021, 0.0],
    [-0.063, -0.021, 0.0], [-0.021, -0.021, 0.0],
    [-0.063, -0.063, 0.0], [-0.021, -0.063, 0.0]
]).T

# Compute STFT, axis=1 is the time axis
f, t, Zxx = stft(data, fs=fs, nperseg=nfft, noverlap=nfft//2, axis=1)
print(f"STFT computed. freq bins: {len(f)}, time frames: {len(t)}")

# Initialize SRP DOA algorithm object, dim=2 means 2D localization
doa = SRP(
    mic_positions,
    fs,
    nfft=nfft,
    c=c,
    azimuth=azimuth_grid,
    elevation=np.array([90]),  # Planar array, elevation fixed at 90 degrees
    dim=2
)

# === Method 1: Locate sources on all time frames at once ===
doa.locate_sources(Zxx)
print("Estimated azimuths (deg) for last frame:", doa.azimuth_recon)

# Plot the DOA energy map for the last frame
plt.figure(figsize=(6,4))
plt.polar(np.deg2rad(azimuth_grid), doa.grid.values)
plt.title("DOA heatmap (SRP-PHAT) - Last Frame")
plt.tight_layout()
plt.show()


# === Method 2: Frame-by-frame processing, output estimated azimuth for each frame ===
print("Frame-by-frame estimated DOA: Zxx.shape[2] =", Zxx.shape[2])
for idx in range(Zxx.shape[2]):
    # Select current frame data, keep 3D shape (channels, freq_bins, 1)
    X = Zxx[:, :, idx:idx+1]
    doa.locate_sources(X)
    print(f"Frame {idx}: azimuths = {doa.azimuth_recon}")

'''
acoustic.py
Convert wav to h5 and show DOA heat map in frequency domain at a given frequency and bandwidth
'''
from os import path
import acoular
import matplotlib.pyplot as plt
import wave
import os

# File paths
wave_file = 'recorded_audio\\drone.wav'
h5_file = 'recorded_audio\\drone.h5'
micgeofile = 'Acoustic_Camera\\minidsp_uma-16.xml'

# Show wav file info
with wave.open(wave_file, 'rb') as wf:
    print("Channels:", wf.getnchannels())
    print("Sample width:", wf.getsampwidth())
    print("Sample rate:", wf.getframerate())
    print("Total frames:", wf.getnframes())

# Convert wav to Acoular-compatible h5
if os.path.exists(h5_file):
    print("H5 file already exists.")
else:
    from scipy.io import wavfile
    import tables

    fs, data = wavfile.read(wave_file)

    acoularh5 = tables.open_file(h5_file, mode="w", title="audio")
    acoularh5.create_earray(
        '/', 'time_data', atom=None, title='', filters=None,
        expectedrows=100000, chunkshape=[256, 64],
        byteorder=None, createparents=False, obj=data
    )
    acoularh5.set_node_attr('/time_data', 'sample_freq', fs)
    acoularh5.close()

# Beamforming processing
mg = acoular.MicGeom(from_file=micgeofile)
ts = acoular.TimeSamples(name=h5_file)
ps = acoular.PowerSpectra(time_data=ts, block_size=128, window='Hanning')
rg = acoular.RectGrid(x_min=-0.2, x_max=0.2, y_min=-0.2, y_max=0.2, z=0.3, increment=0.01)
st = acoular.SteeringVector(grid=rg, mics=mg)
bb = acoular.BeamformerBase(freq_data=ps, steer=st)
pm = bb.synthetic(8000, 3)  # Frequency = 8000 Hz, bandwidth = 3 Hz
Lm = acoular.L_p(pm)

# Plot microphone geometry
plt.figure(figsize=(5, 5))
plt.plot(mg.mpos[0], mg.mpos[1], 'o', label='Microphones')
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Microphone Geometry')
plt.axis('equal')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Plot DOA heat map with axis units
plt.figure(figsize=(6, 5))
img = plt.imshow(
    Lm.T,
    origin='lower',
    vmin=Lm.max() - 3,
    extent=rg.extend(),
    interpolation='bicubic',
    cmap='inferno'
)
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('DOA Heat Map at 8000 Hz ± 3 Hz')
plt.colorbar(img, label='Sound pressure Level [dB]')
plt.tight_layout()
plt.show()

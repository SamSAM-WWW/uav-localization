'''
acoustic.py
convert wav to h5 and show DOA heat map in freq domain in given freq and bandwidth
'''
from os import path
import acoular
from pylab import figure, plot, axis, imshow, colorbar, show
import wave
import os

wave_file = '/home/jetson/mycode/uav-localization/Acoustic_Camera/recorder_output/records/audio.wav'
h5_file ='/home/jetson/mycode/uav-localization/Acoustic_Camera/recorder_output/records/audio.h5'
micgeofile = '/home/jetson/mycode/uav-localization/Acoustic_Camera/minidsp_uma-16.xml'

# wav file info
with wave.open(wave_file, 'rb') as wf:
    print("Channels:", wf.getnchannels())
    print("Sample width:", wf.getsampwidth())
    print("Sample rate:", wf.getframerate())
    print("Total frames:", wf.getnframes())


if os.path.exists(h5_file):
    os.remove(h5_file)

### convert wav to h5
from scipy.io import wavfile
import tables

#read data from wav
fs, data = wavfile.read(wave_file)

#save_to acoular h5 format
acoularh5 = tables.open_file(h5_file, mode = "w", title = "audio")
acoularh5.create_earray('/','time_data', atom=None, title='', filters=None, \
                         expectedrows=100000, chunkshape=[256,64], \
                         byteorder=None, createparents=False, obj=data)
acoularh5.set_node_attr('/time_data','sample_freq', fs)
acoularh5.close()





# Acoular process DOA heat map in freq domain
mg = acoular.MicGeom(from_file=micgeofile)
ts = acoular.TimeSamples(name=h5_file)
ps = acoular.PowerSpectra(time_data=ts, block_size=128, window='Hanning')
rg = acoular.RectGrid(x_min=-0.2, x_max=0.2, y_min=-0.2, y_max=0.2, z=0.3, increment=0.01)
st = acoular.SteeringVector(grid=rg, mics=mg)
bb = acoular.BeamformerBase(freq_data=ps, steer=st)
pm = bb.synthetic(8000, 3) # freq=8000Hz bandwidth=3Hz
Lm = acoular.L_p(pm)

figure(2, figsize=(5,5))
plot(mg.mpos[0], mg.mpos[1],'o')
axis('equal')
show()

imshow(
    Lm.T, origin='lower',
    vmin=Lm.max()-3,
    extent=rg.extend(),
    interpolation='bicubic'
)
colorbar()
show()

import numpy as np
import acoular
import csv

h5_file = '/home/jetson/mycode/uav-localization/Acoustic_Camera/recorder_output/records/audio.h5'
micgeom_file = '/home/jetson/mycode/uav-localization/Acoustic_Camera/minidsp_uma-16.xml'
output_csv = '/home/jetson/mycode/uav-localization/beamforming_result.csv'

block_size = 1024
hop_size = 512
fs = 16000

mg = acoular.MicGeom(from_file=micgeom_file)

total_samples = acoular.TimeSamples(name=h5_file).numsamples
num_frames = int(np.floor((total_samples - block_size) / hop_size)) + 1
print(f'Total samples: {total_samples}, Number of frames: {num_frames}')

with open(output_csv, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['frame', 'time_sec', 'x', 'y', 'z', 'Lp_dB'])

    for i in range(num_frames):
        start_sample = i * hop_size
        stop_sample = start_sample + block_size

        # MaskedTimeSamples slice for current frame
        mts = acoular.MaskedTimeSamples(name=h5_file, start=start_sample, stop=stop_sample)

        # Power spectrum for current frame
        ps = acoular.PowerSpectra(time_data=mts, block_size=block_size, window='Hanning')

        rg = acoular.RectGrid(x_min=-0.2, x_max=0.2,
                              y_min=-0.2, y_max=0.2,
                              z=0.3,
                              increment=0.01)

        st = acoular.SteeringVector(grid=rg, mics=mg)

        bb = acoular.BeamformerBase(freq_data=ps, steer=st)

        try:
            pm = bb.synthetic(8000, 3)
        except Exception as e:
            print(f'Frame {i} error: {e}')
            continue

        Lm = acoular.L_p(pm)
        max_idx = np.unravel_index(np.nanargmax(Lm), Lm.shape)

        nx = len(np.unique(rg.gpos[0]))
        ny = len(np.unique(rg.gpos[1]))
        idx_flat = max_idx[0] * ny + max_idx[1]

        x = rg.gpos[0, idx_flat]
        y = rg.gpos[1, idx_flat]
        z = rg.gpos[2, idx_flat]
        Lp = Lm[max_idx]
        time_sec = start_sample / fs

        print(f'Frame {i}, Time {time_sec:.3f}s: Max SPL at ({x:.3f}, {y:.3f}, {z:.3f}) with {Lp:.2f} dB')
        writer.writerow([i, time_sec, x, y, z, Lp])



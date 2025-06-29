import os
import numpy as np
import acoular
import matplotlib.pyplot as plt
import cv2

# --- 路径配置 ---
wave_file = '/home/jetson/mycode/uav-localization/Acoustic_Camera/recorder_output/records/audio.wav'
h5_file = '/home/jetson/mycode/uav-localization/Acoustic_Camera/recorder_output/records/audio.h5'
micgeo_file = '/home/jetson/mycode/uav-localization/Acoustic_Camera/minidsp_uma-16.xml'

# 如果已有旧的h5文件，先删掉
if os.path.exists(h5_file):
    os.remove(h5_file)

# 1. WAV转H5（Acoular格式）
from scipy.io import wavfile
import tables

fs, data = wavfile.read(wave_file)
with tables.open_file(h5_file, mode='w', title='audio') as h5f:
    # 创建一个可扩展数组，time_data，形状=(samples, channels)
    # Acoular数据格式是(样本数, 通道数)，注意要转置一下data
    if data.ndim == 1:
        data = data[:, None]  # 保证二维
    # Acoular的time_data数组shape是(samples, channels)
    # data.shape (samples, channels)
    h5f.create_earray('/', 'time_data', atom=tables.Atom.from_dtype(data.dtype),
                      shape=(0, data.shape[1]), filters=None, expectedrows=data.shape[0])
    h5f.root.time_data.append(data)
    h5f.root.time_data._v_attrs['sample_freq'] = fs

print(f'WAV converted to H5: {h5_file}')

# 2. 初始化Acoular对象
mg = acoular.MicGeom(from_file=micgeo_file)
ts = acoular.TimeSamples(name=h5_file)
ps = acoular.PowerSpectra(time_data=ts, block_size=1024, window='Hanning')  # 增大block_size提高频率分辨率
rg = acoular.RectGrid(x_min=-0.2, x_max=0.2, y_min=-0.2, y_max=0.2, z=0.3, increment=0.01)
st = acoular.SteeringVector(grid=rg, mics=mg)
bb = acoular.BeamformerBase(freq_data=ps, steer=st)

# 3. 视频保存参数
output_video = 'beamforming_output.mp4'
frame_rate = 10  # 10帧每秒，适当调节
duration = ts.numsamples / fs  # 音频秒数
total_frames = int(duration * frame_rate)

# 图像大小(像素)，根据网格大小和dpi计算
dpi = 100
fig_size_inches = (5, 5)
fig_w, fig_h = int(fig_size_inches[0]*dpi), int(fig_size_inches[1]*dpi)

# 使用matplotlib绘图并保存为numpy数组的函数
def plot_beamforming(Lm, mg, rg):
    fig, ax = plt.subplots(figsize=fig_size_inches, dpi=dpi)
    im = ax.imshow(Lm.T, origin='lower',
                   vmin=0, vmax=np.max(Lm),
                   extent=rg.extend(),
                   interpolation='bicubic')
    ax.plot(mg.mpos[0], mg.mpos[1], 'wo', markersize=5)  # 麦克风位置
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title('Sound Source Localization')
    fig.colorbar(im, ax=ax, label='Sound Pressure Level (dB)')
    plt.tight_layout()

    # 转换为numpy RGB图像
    fig.canvas.draw()
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close(fig)
    return img

# 4. 打开视频写入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(output_video, fourcc, frame_rate, (fig_w, fig_h))

# 5. 逐帧处理
print(f"Generating video with {total_frames} frames...")
samples_per_frame = int(fs / frame_rate)  # 每帧对应多少采样点

for i in range(total_frames):
    start_sample = i * samples_per_frame
    end_sample = min(start_sample + samples_per_frame, ts.numsamples)

    # 重新定义TimeSamples对象，截取当前帧数据
    ts = acoular.TimeSamples(name=h5_file, start=start_sample, stop=end_sample)

    # 重新计算频谱和波束形成器
    ps = acoular.PowerSpectra(time_data=ts, block_size=1024, window='Hanning')
    bb = acoular.BeamformerBase(freq_data=ps, steer=st)

    # 计算声源定位
    pm = bb.synthetic(freq=8000, navg=3)
    Lm = acoular.L_p(pm)

    # 画图成图片
    frame_img = plot_beamforming(Lm, mg, rg)

    # 转成BGR给opencv写入视频
    frame_bgr = cv2.cvtColor(frame_img, cv2.COLOR_RGB2BGR)
    video_writer.write(frame_bgr)

    print(f"Processed frame {i+1}/{total_frames}")

video_writer.release()
print(f"Video saved as {output_video}")

import numpy as np

def calculate_frame_rate(fs, nperseg, noverlap):
    """
    Calculate STFT frame rate (frames per second)
    Parameters:
        fs: sampling rate (Hz)
        nperseg: window size (samples)
        noverlap: overlap size (samples)
    Returns:
        frame_rate: frames per second (Hz)
        frame_step_sec: time interval per frame (seconds)
    """
    frame_step = nperseg - noverlap
    if frame_step <= 0:
        raise ValueError("Invalid parameters: noverlap must be less than nperseg")
    frame_step_sec = frame_step / fs
    frame_rate = 1 / frame_step_sec
    return frame_rate, frame_step_sec

def next_power_of_two(x):
    """Return the next power of two greater than or equal to x."""
    return 1 << (x - 1).bit_length()

def recommend_params(fs, target_fps, nperseg_list=None):
    """
    Recommend nperseg, noverlap and nfft parameter combinations based on target frame rate.
    By default, tries several common nperseg values.
    """
    if nperseg_list is None:
        nperseg_list = [256, 512, 1024, 2048]

    print(f"Target FPS: {target_fps} Hz, Sampling rate: {fs} Hz\n")
    print(f"{'nperseg':>8} | {'noverlap':>8} | {'Frame rate (Hz)':>15} | {'Frame step (ms)':>15} | {'Suggested nfft':>15}")
    print("-" * 80)
    for nperseg in nperseg_list:
        # Calculate suitable frame_step according to target fps
        frame_step = int(fs / target_fps)
        noverlap = nperseg - frame_step
        if noverlap < 0:
            # frame_step larger than nperseg means target fps is too high to achieve
            print(f"{nperseg:8d} | {'-':>8} | {'-':>15} | {'-':>15} | {'-':>15} (frame_step > nperseg)")
            continue
        
        frame_rate, frame_step_sec = calculate_frame_rate(fs, nperseg, noverlap)
        # Suggest nfft as next power of two >= nperseg
        nfft_suggested = next_power_of_two(nperseg)
        
        print(f"{nperseg:8d} | {noverlap:8d} | {frame_rate:15.2f} | {frame_step_sec*1000:15.2f} | {nfft_suggested:15d}")

if __name__ == "__main__":
    fs = 16000       # sampling rate
    target_fps = 30  # target frame rate

    recommend_params(fs, target_fps)

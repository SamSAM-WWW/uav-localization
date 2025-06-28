# recorder

Proof of concept for capturing video and audio.

## Record video and audio
first link cv2 in the system to venv. As cv2 is already installed in jetson nano.

```
cd ~/mycode/uav-localization/uma16_venv/lib/python3.8/site-packages
```

```
ln -s /usr/lib/python3/dist-packages/cv2.cpython-38-aarch64-linux-gnu.so
```

test in venv
```
python3 -c "import cv2; print(cv2.__version__)"
```

use:

```
cd /home/jetson/mycode/uav-localization/Acoustic_Camera

bash record.sh
```

to stop recording, use
```
ctrl+c
```

## Merge video and audio
```
cd recorder_output/records/
bash merge.sh
```

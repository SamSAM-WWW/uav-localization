# UAV-Localization
This project is for UAV localization with the help of UMA_16.

## 📁The folder `UMA_16` 
This is hardware testing and audio recording by using UMA_16. 

📣Windows users should install driver `miniDSP_UAC2_v4.82_Drivers.7z` first , if not, system crash will occur.

📣Sound problem may occur with VMware, please avoid using Ubuntu on VMware to record sound.

📣Sometimes the UMA_16 will be automatically set as system input or output. This will lead to sound record failure. You better set your other devices as system input and output before recording sound.


## 📁The folder `Acoustic_Camera` 
This is code to track sound source.

## 📁The folder `Sim_ROS2` 
This is code to simulate environment and sound source in gazebo & ROS2 for further development.


These 3 folders are separate.

minidsp_uma-16.xml is the layout location of the microphones on the miniDSP UMA-16
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import sounddevice as sd
import numpy as np

class MicReaderNode(Node):
    def __init__(self):
        super().__init__('mic_reader_node')

        self.fs = 48000
        self.channels = 16
        self.chunk = int(self.fs * 0.1)  # 0.1s/sample
        self.device_index = self.find_input_device("UMA16")  # UMA16 match

        self.get_logger().info(f"Using device index: {self.device_index}")
        self.publisher_ = self.create_publisher(Float32MultiArray, '/mic_array/audio_raw', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

    def find_input_device(self, keyword):
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if keyword.lower() in dev['name'].lower() and dev['max_input_channels'] >= self.channels:
                self.get_logger().info(f"Found matching device at index {i}: {dev['name']}")
                return i
        raise RuntimeError(f"No suitable device found with keyword '{keyword}'")

    def timer_callback(self):
        try:
            audio = sd.rec(frames=self.chunk, samplerate=self.fs, channels=self.channels,
                           device=self.device_index, dtype='float32')
            sd.wait()

            msg = Float32MultiArray()
            msg.data = audio.flatten().tolist()
            self.publisher_.publish(msg)
            self.get_logger().info('Published audio chunk')
        except Exception as e:
            self.get_logger().error(f"Audio capture error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = MicReaderNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
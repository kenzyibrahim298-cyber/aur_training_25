#! /usr/bin/env python3

import rclpy 
from rclpy.node import Node
from std_msgs.msg import Int32

class Monitor_node(Node):
    def __init__(self):
        super().__init__("monitor_node")
        
        self.create_subscription(Int32, '/temperature', self.temp_callback, 10)
        self.create_subscription(Int32, '/humidity', self.humidity_callback, 10)
        self.create_subscription(Int32, '/pressure', self.pressure_callback, 10)
    
        self.file = open("weather_readings.txt", "w")

    def temp_callback(self, msg):
        self.get_logger().info(f"Temperature:{msg.data}°C")
        self.file.write(f"{msg.data}°C\n")
        
    def humidity_callback(self, msg):
        self.get_logger().info(f"Humidity:{msg.data}%")
        self.file.write(f"{msg.data}%\n")

    def pressure_callback(self, msg):
        self.get_logger().info(f"Pressure:{msg.data}hPa")
        self.file.write(f"{msg.data}hPa\n")

    def destroy_node(self):
        self.file.close()
        super().destroy_node()

def main():
    rclpy.init()
    node = Monitor_node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

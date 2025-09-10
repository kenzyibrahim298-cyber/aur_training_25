#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from random import randint

class Temperature_node(Node):
    def __init__(self):
        super().__init__("temperature_node")
        self.get_logger().info("temp node started!")
        self.temp_node = self.create_publisher(Int32, '/temperature', 10)
        self.create_timer(1, self.timer_callback)

    def timer_callback(self):
        msg = Int32()
        msg.data = randint(15, 40)
        self.temp_node.publish(msg)
        self.get_logger().info(f"{msg.data}")

def main():
    rclpy.init()
    node = Temperature_node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    
    


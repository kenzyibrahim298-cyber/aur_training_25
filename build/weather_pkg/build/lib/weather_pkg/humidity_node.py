#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from random import randint

class Humidity_node(Node):
    def __init__(self):
        super().__init__("humidity_node")
        self.get_logger().info("Humidity node started!")
        self.humidity_node = self.create_publisher(Int32, '/humidity', 10)
        self.create_timer(2, self.timer_callback)

    def timer_callback(self):
        msg = Int32()
        msg.data = randint(20, 100)
        self.humidity_node.publish(msg)
        self.get_logger().info(f"{msg.data}")



def main():
    rclpy.init()
    node = Humidity_node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
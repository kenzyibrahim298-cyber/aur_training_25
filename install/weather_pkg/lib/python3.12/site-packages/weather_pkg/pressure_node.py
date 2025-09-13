#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from random import randint

class Pressure_node(Node):
    def __init__(self):
        super().__init__("pressure_node")
        self.get_logger().info("pressure node started!")
        self.pressure_node = self.create_publisher(Int32, '/pressure', 10)
        self.create_timer(3, self.timer_callback)

    def timer_callback(self):
        msg = Int32()
        msg.data = randint(900, 1100)
        self.pressure_node.publish(msg)
        self.get_logger().info(f"{msg.data}")

def main():
    rclpy.init()
    node = Pressure_node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

#! /usr/bin/env python3

import rclpy
from rclpy.node import Node

class timer_node(Node):
    def __init__(self):
        super().__init__("timer_node")
        self.get_logger().info("Timer started!")
        self.counter = 10
        self.create_timer(1, self.timer_callback)
        

    def timer_callback(self):
        self.get_logger().info(f"{self.counter}")
        if(self.counter == 0):
            self.get_logger().info("Time is up!")
            rclpy.shutdown()
        self.counter = self.counter - 1

def main():
    rclpy.init()
    node = timer_node()
    rclpy.spin(node)
    node.destroy_node()
        

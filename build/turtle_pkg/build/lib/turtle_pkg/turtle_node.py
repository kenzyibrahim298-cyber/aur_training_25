#! /usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class Move_turtle2(Node):
    def __init__(self):
        super().__init__('turtle_node')
        self.pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
    
    def move(self, key):
        msg = Twist()

        if key == 'w':
            msg.linear.x = 2.0
        elif key == 's':
            msg.linear.x = -2.0
        elif key == 'a':
            msg.angular.z = 2.0
        elif key == 'd':
            msg.angular.z = -2.0

        self.pub.publish(msg)

def main():
    rclpy.init()
    node = Move_turtle2()

    try:
        while True:
            key = input(">> ").lower()
            if key == 'q':
                break
            node.move(key)

    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()


    

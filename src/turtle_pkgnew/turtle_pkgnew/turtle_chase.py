#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from turtlesim_msgs.srv import Spawn, Kill
from turtlesim_msgs.msg import Pose
from std_msgs.msg import  Int32
import random 
import math 
from functools import partial 

class Turtle_chase(Node):
    def __init__(self):
        super().__init__('turtle_chase')

        self.score_pub = self.create_publisher(Int32, '/score', 10)
        self.score = 0

        self.spawn_client = self.create_client(Spawn, '/spawn')
        self.kill_client = self.create_client(Kill, '/kill')

        self.spawn_client.wait_for_service()
        self.kill_client.wait_for_service()

        self.player_pose = None
        self.create_subscription(Pose, '/turtle1/pose', self.player_callback, 10)

        self.enemy_positions = {}
        self.enemies = ['enemy1', 'enemy2', 'enemy3']
        for name in self.enemies:
            self.spawn_enemy(name)
            self.create_subscription(Pose, f'/{name}/pose', partial(self.enemy_callback, name=name), 10)

        self.create_timer(0.1, self.check_collisions)

    def player_callback(self, msg: Pose):
        self.player_pose = msg

    def enemy_callback(self, msg: Pose, name: str):
        self.enemy_positions[name] = msg

    def spawn_enemy(self, name: str):
        req = Spawn.Request()
        req.x = random.uniform(3.0, 8.0)
        req.y = random.uniform(3.0, 8.0)
        req.theta = 0.0
        req.name = name
        future = self.spawn_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

    def kill_enemy(self, name: str):
        req = Kill.Request()
        req.name = name
        self.kill_client.call_async(req)
        
    def find_distance(self, p1:Pose, p2:Pose):
        return math.sqrt((p1.x - p2.x ) ** 2 + (p1.y - p2.y) ** 2)
        
    def check_collisions(self):
        if self.player_pose is None:
            return
        for name, pose in list(self.enemy_positions.items()):
            dist = self.find_distance(self.player_pose, pose)
            if dist < 0.5:
                self.get_logger().info(f'{name} was hit')
                self.kill_enemy(name)
                self.spawn_enemy(name)
                self.score += 1
                msg = Int32()
                msg.data = self.score
                self.score_pub.publish(msg)
                self.get_logger().info(f'THE SCORE IS {self.score}')


def main(args=None):
    rclpy.init(args=args)
    node = Turtle_chase()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

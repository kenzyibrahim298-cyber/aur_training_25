import math
import struct
 
import rclpy
from rclpy.node import Node
 
from std_msgs.msg import Bool, Float32MultiArray
from sensor_msgs.msg import Imu, NavSatFix, NavSatStatus
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
 
from stm32 import STM32
from stm_msgs import (
    PacketType, PAYLOAD_FMT,
    frame_wheel_vel, frame_laser, frame_servo_angles,
    frame_operation_mode, frame_antenna_angle,
)
 
 

WHEEL_RADIUS  = 0.05    
WHEEL_BASE    = 0.30    
TICKS_PER_REV = 1024    
 
 
def ticks_to_metres(ticks: float) -> float:
    return (ticks / TICKS_PER_REV) * (2 * math.pi * WHEEL_RADIUS)
 
 

class STM32Node(Node):
 
    def __init__(self):
        super().__init__('stm32_node')
 
        
        self.declare_parameter('port',     '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 115200)
        self.declare_parameter('timer_hz', 50.0)
 
        port     = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value
        hz       = self.get_parameter('timer_hz').value
 
        
        self.stm = STM32(baudrate=baudrate)
        self.stm.connect(port)
 
        
        self.pub_imu     = self.create_publisher(Imu,               '/imu/data',       10)
        self.pub_gps     = self.create_publisher(NavSatFix,         '/gps/fix',        10)
        self.pub_odom    = self.create_publisher(Odometry,          '/odom',           10)
        self.pub_status  = self.create_publisher(Float32MultiArray, '/stm32/status',   10)
        self.pub_antenna = self.create_publisher(NavSatFix,         '/stm32/antenna',  10)
 
        
        self.create_subscription(Twist,            '/cmd_vel',            self._cb_cmd_vel, 10)
        self.create_subscription(Bool,             '/stm32/cmd_laser',    self._cb_laser,   10)
        self.create_subscription(Float32MultiArray,'/stm32/cmd_servo',    self._cb_servo,   10)
        self.create_subscription(Bool,             '/stm32/cmd_mode',     self._cb_mode,    10)
        self.create_subscription(Float32MultiArray,'/stm32/cmd_antenna',  self._cb_antenna, 10)
 
        
        self._odom_x:   float = 0.0
        self._odom_y:   float = 0.0
        self._odom_yaw: float = 0.0
 
       
        self.create_timer(1.0 / hz, self._timer_cb)
        self.get_logger().info(f'STM32 node started — {port} @ {baudrate} baud, {hz} Hz')
 
    
    def _timer_cb(self):
        while True:
            result = self.stm.read_frame()
            if result is None:
                break
            pkt_type, payload = result
            self._dispatch(pkt_type, payload)
 
    
    def _dispatch(self, pkt_type: PacketType, payload: bytes):
        try:
            if pkt_type == PacketType.IMU:
                self._handle_imu(payload)
            elif pkt_type == PacketType.GPS:
                self._handle_gps(payload)
            elif pkt_type == PacketType.ENCODERS:
                self._handle_encoders(payload)
            elif pkt_type == PacketType.STATUS:
                self._handle_status(payload)
            elif pkt_type == PacketType.ANTENNA:
                self._handle_antenna(payload)
        except struct.error as e:
            self.get_logger().warn(f'Parse error for {pkt_type.name}: {e}')
 
    
    def _handle_imu(self, payload: bytes):
        """IMU packet: q1 q2 q3 q4  α β ψ  ẋ ẏ ż  (10 floats)"""
        vals = struct.unpack(PAYLOAD_FMT[PacketType.IMU], payload)
        q1, q2, q3, q4, alpha, beta, psi, xd, yd, zd = vals
 
        msg = Imu()
        msg.header.stamp    = self.get_clock().now().to_msg()
        msg.header.frame_id = 'imu_link'
        msg.orientation.x = float(q1)
        msg.orientation.y = float(q2)
        msg.orientation.z = float(q3)
        msg.orientation.w = float(q4)
        msg.angular_velocity.x    = float(alpha)
        msg.angular_velocity.y    = float(beta)
        msg.angular_velocity.z    = float(psi)
        msg.linear_acceleration.x = float(xd)
        msg.linear_acceleration.y = float(yd)
        msg.linear_acceleration.z = float(zd)
        self.pub_imu.publish(msg)
 
    def _handle_gps(self, payload: bytes):
        """GPS packet: long lat cov[9]  (11 floats)"""
        vals = struct.unpack(PAYLOAD_FMT[PacketType.GPS], payload)
        msg = NavSatFix()
        msg.header.stamp    = self.get_clock().now().to_msg()
        msg.header.frame_id = 'gps_link'
        msg.status.status   = NavSatStatus.STATUS_FIX
        msg.status.service  = NavSatStatus.SERVICE_GPS
        msg.longitude       = float(vals[0])
        msg.latitude        = float(vals[1])
        msg.altitude        = 0.0
        msg.position_covariance      = [float(v) for v in vals[2:]]
        msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_KNOWN
        self.pub_gps.publish(msg)
 
    def _handle_encoders(self, payload: bytes):
        """
        ENCODERS packet: FL BL FR BR (4 floats — raw ticks since last packet).
        Computes differential-drive odometry and publishes to /odom.
        """
        fl, bl, fr, br = struct.unpack(PAYLOAD_FMT[PacketType.ENCODERS], payload)
 
        d_left  = ticks_to_metres((fl + bl) / 2.0)
        d_right = ticks_to_metres((fr + br) / 2.0)
        d_centre = (d_left + d_right) / 2.0
        d_yaw    = (d_right - d_left) / WHEEL_BASE
 
        self._odom_x   += d_centre * math.cos(self._odom_yaw + d_yaw / 2.0)
        self._odom_y   += d_centre * math.sin(self._odom_yaw + d_yaw / 2.0)
        self._odom_yaw += d_yaw
 
        cy = math.cos(self._odom_yaw / 2.0)
        sy = math.sin(self._odom_yaw / 2.0)
 
        odom = Odometry()
        odom.header.stamp    = self.get_clock().now().to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id  = 'base_link'
        odom.pose.pose.position.x    = self._odom_x
        odom.pose.pose.position.y    = self._odom_y
        odom.pose.pose.orientation.z = float(sy)
        odom.pose.pose.orientation.w = float(cy)
        self.pub_odom.publish(odom)
 
    def _handle_status(self, payload: bytes):
        """STATUS: bat1 bat2_4 cur[4] srv1 srv2 flags"""
        vals = struct.unpack(PAYLOAD_FMT[PacketType.STATUS], payload)
        msg = Float32MultiArray()
        msg.data = [float(v) for v in vals]
        self.pub_status.publish(msg)
 
    def _handle_antenna(self, payload: bytes):
        vals = struct.unpack(PAYLOAD_FMT[PacketType.ANTENNA], payload)
        msg = NavSatFix()
        msg.header.stamp    = self.get_clock().now().to_msg()
        msg.header.frame_id = 'antenna_link'
        msg.longitude = float(vals[0])
        msg.latitude  = float(vals[1])
        self.pub_antenna.publish(msg)
 

    def _cb_cmd_vel(self, msg: Twist):
        """Convert (v, ω) → (v_left, v_right) and send WHEEL_VEL packet."""
        v     = msg.linear.x
        omega = msg.angular.z
        self.stm.send_frame(frame_wheel_vel(
            v - omega * WHEEL_BASE / 2.0,
            v + omega * WHEEL_BASE / 2.0,
        ))
 
    def _cb_laser(self, msg: Bool):
        self.stm.send_frame(frame_laser(msg.data))
 
    def _cb_servo(self, msg: Float32MultiArray):
        if len(msg.data) != 2:
            self.get_logger().warn('servo needs [servo1, servo2]')
            return
        self.stm.send_frame(frame_servo_angles(*msg.data))
 
    def _cb_mode(self, msg: Bool):
        self.stm.send_frame(frame_operation_mode(msg.data))
 
    def _cb_antenna(self, msg: Float32MultiArray):
        if len(msg.data) != 1:
            self.get_logger().warn('antenna_angle needs [angle]')
            return
        self.stm.send_frame(frame_antenna_angle(msg.data[0]))
 
    
    def destroy_node(self):
        self.stm.disconnect()
        super().destroy_node()
 
 

def main(args=None):
    rclpy.init(args=args)
    node = STM32Node()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
 
 
if __name__ == '__main__':
    main()
 

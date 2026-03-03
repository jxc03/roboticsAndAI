#!/usr/bin/env python3
"""
Commands the leader turtle to turn to a random direction then move
forward until hitting the boundary. Publishes the custom LeaderMessage

References:
- W2 Practical Part C:
- W2 Lecture: Publisher, Subscriber patterns
- W4 Practical Part A: 
"""

import rospy
import random
import math
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from com760cw1_b00835055.msg import B00835055LeaderMessage

class LeaderNode:
    def __init__(self):
    	# Initialise ROS node
        rospy.init_node('leader_node')

        # Get leader name from parameter or use default
        self.leader_name = rospy.get_param('~leader_name', 'B00835055Leader')

        # Current pose of the leader
        self.pose = None

        # Boundary limits (turtlesim is ~11x11, stay away from edges)
        self.BOUNDARY_MIN = 0.5
        self.BOUNDARY_MAX = 10.5

        # Publisher for velocity commands
        # Source: W2 Lecture
        self.vel_pub = rospy.Publisher(
            '/%s/cmd_vel' % self.leader_name, Twist, queue_size=10)

        # Publisher for custom leader message (followers subscribe to this)
        self.leader_msg_pub = rospy.Publisher(
            '/leader_message', B00835055LeaderMessage, queue_size=10)

        # Subscribe to leaders pose to monitor position
        # Source: W2 Practical
        rospy.Subscriber(
            '/%s/pose' % self.leader_name, Pose, self.pose_callback)

        # Wait for first pose
        rospy.loginfo("Leader node waiting for pose data...")
        while self.pose is None and not rospy.is_shutdown():
            rospy.sleep(0.1)

        rospy.loginfo("Leader node started for: %s", self.leader_name)
        self.run()
    
    # Store the latest pose from the turtlesim
    def pose_callback(self, data):
        self.pose = data # Store 
        
    # Publish a custom leader message on the /leader_message topic
    # Source: W3 Practical Part C - custom message definition
    # instructionID: 0 = Formation, 1 = Return # 0 = Formation mode, 1 = Return / Boundary hit
    def publish_leader_message(self, instruction_id, message):
        msg = B00835055LeaderMessage()
        msg.instructionID = instruction_id
        msg.message = message
        self.leader_msg_pub.publish(msg)

    # Check if the leader is close to any wall
    def is_near_boundary(self):
        if self.pose is None:
            return False
        return (self.pose.x <= self.BOUNDARY_MIN or
                self.pose.x >= self.BOUNDARY_MAX or
                self.pose.y <= self.BOUNDARY_MIN or
                self.pose.y >= self.BOUNDARY_MAX)
                
    # Turn the leader to face a specific angle
    # Uses the proportional controller for angular velocity
    # Source: W2 Lecture - Proportional controller for angular velocity
    def turn_to_angle(self, target_angle):
        rate = rospy.Rate(10)
        Kh = 6.0 # Angular gain

        while not rospy.is_shutdown():
            # Angle difference between target and current heading
            angle_diff = target_angle - self.pose.theta
            # Normalise to [-pi, pi]
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
	    
	    # Stop turning when close enough
            if abs(angle_diff) < 0.05: # Close enough
                self.vel_pub.publish(Twist()) # Stop rotation
                return
            
            # Apply proportional angular velocity
            vel_msg = Twist()
            vel_msg.angular.z = Kh * angle_diff
            self.vel_pub.publish(vel_msg)
            rate.sleep()
            
    # Main loop: turn to random direction, move forward until boundary then repeat.
    # Source: W4 Practical Part A
    def run(self):
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            # Phase 1: Turn to a random direction
            random_angle = random.uniform(-math.pi, math.pi)
            rospy.loginfo("Leader turning to angle: %.2f radians", random_angle)
            self.publish_leader_message(0, "Turning to new direction")
            self.turn_to_angle(random_angle)

            # Phase 2: Move forward until hitting boundary
            rospy.loginfo("Leader moving forward in formation mode")
            self.publish_leader_message(0, "Formation mode - moving forward")

            while not rospy.is_shutdown() and not self.is_near_boundary():
                vel_msg = Twist()
                vel_msg.linear.x = 2.0 # Forward speed
                self.vel_pub.publish(vel_msg)

                # Keep publishing the leader message so followers know the state
                self.publish_leader_message(0, "Formation mode - moving forward")
                rate.sleep()

            # Phase 3: Hit boundary, stop and notify
            self.vel_pub.publish(Twist()) # Stop movement
            rospy.loginfo("Leader hit boundary at (%.2f, %.2f)",
                          self.pose.x, self.pose.y)
            self.publish_leader_message(1, "Hit boundary - changing direction")
            rospy.sleep(1) # Brief pause before turn  ing again

if __name__ == '__main__':
    try:
        LeaderNode()
    except rospy.ROSInterruptException:
        pass

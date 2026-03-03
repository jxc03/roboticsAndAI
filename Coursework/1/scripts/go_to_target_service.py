#!/usr/bin/env python3
"""
Provides a service that moves a named turtle to a goal position using a proportional controller

References:
- W2 Lecture: Proportional controller for linear speed and angular velocity
- W3 Practical Part B: Navigation as a service (TurtleGoal.srv)
- W4 Lecture Slide 26: The Proportional Controller with tf
- ROS Wiki: http://wiki.ros.org/turtlesim/Tutorials/Go%20to%20Goal
"""

import rospy
import math
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from com760cw1_b00835055.srv import B00835055GoToTarget, B00835055GoToTargetResponse

class GoToTargetService:
    def __init__(self):
        # Initialise the ROS node for this service
        rospy.init_node('go_to_target_service')

        # Current pose storage which is updated by subscriber callbacks
        self.poses = {} # Dictionary storing latest pose for each turtle

        # Register the service
        # Source: W3 Lecture
        rospy.Service('go_to_target', B00835055GoToTarget, self.handle_go_to_target) # Call "go_to_target" with turtle name & goal
        rospy.loginfo("Go-to-target service is ready")
        rospy.spin() # Keep the node alive
    
    # Callback that stores the latest pose for a given turtle
    def pose_callback(self, data, turtle_name):
        self.poses[turtle_name] = data # Store
        
    # Service handler to move requested turtle to the goal position
    def handle_go_to_target(self, req):
        turtle_name = req.turtle_name
        goal_x = req.goal_x
        goal_y = req.goal_y
        tolerance = req.tolerance

        rospy.loginfo("Request: Move %s to (%.2f, %.2f) with tolerance %.2f",
                      turtle_name, goal_x, goal_y, tolerance)

        # Validate the goal, must be within turtlesim bounds (0 to 11)
        # Source:
        if goal_x < 0 or goal_x > 11 or goal_y < 0 or goal_y > 11:
            rospy.logwarn("Goal (%.2f, %.2f) is outside turtlesim bounds!", goal_x, goal_y)
            return B00835055GoToTargetResponse(False)

        # Subscribe to this turtle's pose topic
        # Each turtle has its own /turtleName/pose topic
        rospy.Subscriber('/%s/pose' % turtle_name, Pose,
                         self.pose_callback, turtle_name)

        # Create a publisher for this turtle's velocity commands
        pub = rospy.Publisher('/%s/cmd_vel' % turtle_name, Twist, queue_size=10)

        # Wait until the first pose is received
        rate = rospy.Rate(10)
        while turtle_name not in self.poses and not rospy.is_shutdown():
            rate.sleep()

        # Proportional controller
        # Source: W2 Lecture 
        # The formulas from the lecture slide:
        # theta* = atan2(y* - y, x* - x)       (desired heading)
        # v = Kv * sqrt((x*-x)^2 + (y*-y)^2)   (linear speed)
        # omega = Kh * (theta* - theta)        (angular speed)
        #
        # Kv and Kh are proportional gain constants
        # Larger values = faster but less stable movement

        Kv = 1.5 # Linear speed gain
        Kh = 6.0 # Angular speed gain

        while not rospy.is_shutdown():
            pose = self.poses[turtle_name]

            # Calculate distance to goal (Euclidean distance)
            distance = math.sqrt((goal_x - pose.x) ** 2 + (goal_y - pose.y) ** 2)

            # Check if close enough
            if distance < tolerance:
                # Stop the turtle
                pub.publish(Twist())
                rospy.loginfo("%s reached goal (%.2f, %.2f)!", turtle_name, goal_x, goal_y)
                return B00835055GoToTargetResponse(True)

            # Calculate desired heading angle using atan2
            # Source: W2 Lecture
            # Source: W4 Lecture Slide 26
            desired_angle = math.atan2(goal_y - pose.y, goal_x - pose.x)

            # Calculate the angle difference
            angle_diff = desired_angle - pose.theta

            # Normalise angle to [-pi, pi] to prevent spinning the long way round
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

            # Apply proportional controller
            vel_msg = Twist()
            vel_msg.linear.x = Kv * distance # Move faster whem far away
            vel_msg.angular.z = Kh * angle_diff # Rotate proportionally to angle error

            # Clamp linear speed to prevent the turtle going too fast
            vel_msg.linear.x = min(vel_msg.linear.x, 3.0)
	    
	    # Publish velocity command
            pub.publish(vel_msg)
            rate.sleep()

        return B00835055GoToTargetResponse(False)

if __name__ == '__main__':
    try:
        GoToTargetService()
    except rospy.ROSInterruptException:
        pass

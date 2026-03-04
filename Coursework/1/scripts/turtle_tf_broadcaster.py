#!/usr/bin/env python3
"""
Broadcasts a turtle's pose as a tf2 coordinate frame
One instance per turtle, parameterised by turtle_name

References:
- W4Lecture: "ROS tf2 System - Broadcaster"
- W4Lecture: "Writing a tf2 broadcaster - Quaternion"
- W4Lecture: "Steps to broadcast transforms using ROS"
- ROS Wiki: http://wiki.ros.org/tf2/Tutorials/Writing%20a%20tf2%20broadcaster%20(Python)
"""

import rospy
import tf2_ros
import tf.transformations
from geometry_msgs.msg import TransformStamped
from turtlesim.msg import Pose

# Callback to receive a Pose message and broadcasts it as a tf2 transform
def handle_turtle_pose(msg, turtle_name):
    # Create a TransformStamped message
    t = TransformStamped()

    # Header for timestamp and parent frame
    t.header.stamp = rospy.Time.now()
    t.header.frame_id = 'world'  # Parent frame

    # Child frame for turtle's own frame
    t.child_frame_id = turtle_name

    # Translation for the turtle's (x, y) position
    t.transform.translation.x = msg.x
    t.transform.translation.y = msg.y
    t.transform.translation.z = 0.0 # is 0 because turtlesim is 2D

    # Rotation for converting the turtle's theta (yaw) to a quaternion
    # In 2D turtlesim: roll=0, pitch=0, yaw=theta
    q = tf.transformations.quaternion_from_euler(0, 0, msg.theta)
    t.transform.rotation.x = q[0]
    t.transform.rotation.y = q[1]
    t.transform.rotation.z = q[2]
    t.transform.rotation.w = q[3]

    # Broadcast the transform
    br.sendTransform(t)


if __name__ == '__main__':
    rospy.init_node('turtle_tf2_broadcaster')

    # Get the turtle name from the private parameter
    turtle_name = rospy.get_param('~turtle_name', 'turtle1')

    # Create the broadcaster
    br = tf2_ros.TransformBroadcaster()

    # Subscribe to the turtle's pose topic
    # The callback receives both the Pose message and the turtle_name
    rospy.Subscriber('/%s/pose' % turtle_name, Pose,
                     handle_turtle_pose, turtle_name)

    rospy.loginfo("Broadcasting tf for: %s", turtle_name)
    rospy.spin()

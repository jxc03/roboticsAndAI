#!/usr/bin/env python3
"""
Creates offset frames relative to the leader for formation control
Each follower tracks its own carrot frame instead of the leader directly

References:
- W4 Lecture: "Adding a frame to tf - Leader-follower formation"
- W4 Lecture: "How to add a frame?"
- ROS Wiki: https://wiki.ros.org/tf2/Tutorials/Adding%20a%20frame%20(Python)
"""

import rospy
import tf2_ros
import math
from geometry_msgs.msg import TransformStamped


def broadcast_carrot_frames():
    # Initialise ROS node for broadcasting carrot frames
    rospy.init_node('carrot_frame_broadcaster')

    # TF broadcaster object for sending transforms
    br = tf2_ros.TransformBroadcaster()

    # Formation offsets relative to the leader
    # These define the formation shape
    # Negative x = behind the leader, y = left/right offset
    carrot_offsets = {
        'carrot_followerA': {'x': -2.0, 'y': 1.5}, # Behind and to the left
        'carrot_followerB': {'x': -2.0, 'y': -1.5}, # Behind and to the right
    }

    # Broadcast
    rate = rospy.Rate(10) # Currently at 10 Hz

    while not rospy.is_shutdown():
        # Create and broadcast a transform for each carrot frame
        for carrot_name, offset in carrot_offsets.items():
            t = TransformStamped()

            # Timestamp TF synchronisation
            t.header.stamp = rospy.Time.now()

            # Parent frame is the LEADER
            # Carrot moves WITH the leader
            t.header.frame_id = 'B00835055Leader'

            # Child frame, the carrot frame for a follower
            t.child_frame_id = carrot_name

            # Offset position relative to the leader
            # x offset: negative means BEHIND the leader
            # y offset: positive means to the LEFT, negative to the RIGHT
            t.transform.translation.x = offset['x']
            t.transform.translation.y = offset['y']
            t.transform.translation.z = 0.0

            # No additional rotation, carrot faces same direction as leader
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = 1.0 # Identity quaternion = no rotation

            # Broadcast the transform
            br.sendTransform(t)

        rate.sleep()


if __name__ == '__main__':
    try:
        broadcast_carrot_frames()
    except rospy.ROSInterruptException:
        pass

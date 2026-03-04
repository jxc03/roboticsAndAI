#!/usr/bin/env python3
"""
follower_node.py - CW1 Follower Control Node
Uses tf2 listener to track the assigned carrot frame and navigate
towards it. Responds to leader instructions (Formation/Return).

References:
- W4 Lecture Slide 24: "Writing a tf2 listener in Python"
- W4 Lecture Slide 26: "The Proportional Controller" with tf
- W4 Lecture Slide 47: "Adding a frame to tf2" (follower chases carrot)
- CW1 Spec Steps 4-7
"""
import rospy
import tf2_ros
import math
from geometry_msgs.msg import Twist
from com760cw1_b00835055.msg import B00835055LeaderMessage


class FollowerNode:
    def __init__(self):
        rospy.init_node('follower_node', anonymous=True)

        self.follower_name = rospy.get_param('~follower_name', 'B00835055FollowerA')
        self.carrot_frame = rospy.get_param('~carrot_frame', 'carrot_followerA')

        # Leader instruction: 0=Formation, 1=Return
        self.leader_instruction = -1  # No instruction yet

        # Proportional controller gains
        # Source: W4 Lecture Slide 26
        self.Kv = 0.5
        self.Kh = 4.0

        # Publisher for velocity commands
        self.vel_pub = rospy.Publisher(
            '/%s/cmd_vel' % self.follower_name, Twist, queue_size=10)

        # Subscribe to leader messages
        rospy.Subscriber('/leader_message', B00835055LeaderMessage,
                         self.leader_msg_callback)

        # tf2 listener
        self.tfBuffer = tf2_ros.Buffer()
        self.listener = tf2_ros.TransformListener(self.tfBuffer)

        rospy.loginfo("Follower %s tracking carrot frame: %s",
                      self.follower_name, self.carrot_frame)

        rospy.sleep(2)
        self.run()

    def leader_msg_callback(self, msg):
        self.leader_instruction = msg.instructionID

    def run(self):
        """
        Main loop: follow carrot frame when in Formation mode (0),
        stop when in Return mode (1).
        """
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            # Only follow when leader says Formation (instructionID=0)
            if self.leader_instruction == 1:
                # Return instruction — stop moving, leader will teleport us
                self.vel_pub.publish(Twist())
                rate.sleep()
                continue

            if self.leader_instruction == -1:
                # No instruction received yet — wait
                rate.sleep()
                continue

            try:
                # Look up transform from follower to its carrot frame
                trans = self.tfBuffer.lookup_transform(
                    self.follower_name,
                    self.carrot_frame,
                    rospy.Time())

                dx = trans.transform.translation.x
                dy = trans.transform.translation.y
                distance = math.sqrt(dx ** 2 + dy ** 2)

                vel_msg = Twist()

                if distance > 0.3:
                    # Source: W4 Lecture Slide 26:
                    # angular = 4 * math.atan2(trans[1], trans[0])
                    # linear = 0.5 * math.sqrt(trans[0]**2 + trans[1]**2)
                    vel_msg.angular.z = self.Kh * math.atan2(dy, dx)
                    vel_msg.linear.x = min(self.Kv * distance, 3.0)
                else:
                    vel_msg.linear.x = 0.0
                    vel_msg.angular.z = 0.0

                self.vel_pub.publish(vel_msg)

            except (tf2_ros.LookupException,
                    tf2_ros.ConnectivityException,
                    tf2_ros.ExtrapolationException):
                rate.sleep()
                continue

            rate.sleep()


if __name__ == '__main__':
    try:
        FollowerNode()
    except rospy.ROSInterruptException:
        pass

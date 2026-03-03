#!/usr/bin/env python3
"""
Implements the cycle:
  Step 4: Send 'Formation' instruction, wait for followers
  Step 5: Turn random direction, move with red pen until boundary
  Step 7: Send 'Return' instruction, teleport followers, use GoToTarget
          service for leader to return to centre, white pen
  Step 8: Clear screen, repeat from Step 4

References:
- W2 Lecture: Publisher, Subscriber, Proportional controller
- W4 Practical: Leader movement and boundary detection
- CW1 Spec Steps 4-8
"""

import rospy
import random
import math
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import SetPen, TeleportAbsolute
from std_srvs.srv import Empty
from com760cw1_b00835055.msg import B00835055LeaderMessage
from com760cw1_b00835055.srv import B00835055GoToTarget

# Initialises the leader node, loads parameters, subscribes to poses,
# stores initial follower positions and starts the main cycle
class LeaderNode:
    def __init__(self):
        rospy.init_node('leader_node')

        # Turtle names
        self.leader_name = rospy.get_param('~leader_name', 'B00835055Leader')
        self.followerA_name = 'B00835055FollowerA'
        self.followerB_name = 'B00835055FollowerB'

        # Pose storage, updates by callbacks
        self.pose = None
        self.followerA_pose = None
        self.followerB_pose = None

        # Store initial spawn positions of followers, set after first pose received
        self.followerA_initial = None
        self.followerB_initial = None

        # Boundary limits
        self.BOUNDARY_MIN = 0.5
        self.BOUNDARY_MAX = 10.5

        # Leader centre position
        self.CENTRE_X = 5.544
        self.CENTRE_Y = 5.544

        # Movement parameters
        self.FORWARD_SPEED = 2.0
        self.TURN_GAIN = 6.0

        self.boundary_hit_count = 0

        # Publishers
        self.vel_pub = rospy.Publisher(
            '/%s/cmd_vel' % self.leader_name, Twist, queue_size=10)
        self.leader_msg_pub = rospy.Publisher(
            '/leader_message', B00835055LeaderMessage, queue_size=10)

        # Subscribers for all turtle poses
        rospy.Subscriber('/%s/pose' % self.leader_name, Pose, self.leader_pose_cb)
        rospy.Subscriber('/%s/pose' % self.followerA_name, Pose, self.followerA_pose_cb)
        rospy.Subscriber('/%s/pose' % self.followerB_name, Pose, self.followerB_pose_cb)

        # Wait for all poses
        rospy.loginfo("Leader node waiting for all turtle poses...")
        while (self.pose is None or self.followerA_pose is None or
               self.followerB_pose is None) and not rospy.is_shutdown():
            rospy.sleep(0.1)

        # Store initial follower positions for teleporting back later
        # CW1 Step 7: "Teleport 2 followers to their initial position"
        self.followerA_initial = {
            'x': self.followerA_pose.x,
            'y': self.followerA_pose.y,
            'theta': self.followerA_pose.theta
        }
        self.followerB_initial = {
            'x': self.followerB_pose.x,
            'y': self.followerB_pose.y,
            'theta': self.followerB_pose.theta
        }
        rospy.loginfo("Stored initial positions - FollowerA: (%.2f, %.2f), FollowerB: (%.2f, %.2f)",
                      self.followerA_initial['x'], self.followerA_initial['y'],
                      self.followerB_initial['x'], self.followerB_initial['y'])

        rospy.loginfo("Leader node started. Beginning formation cycle.")
        self.run_cycle()

    # Pose callbacks
    def leader_pose_cb(self, data):
        self.pose = data # Store leader
    def followerA_pose_cb(self, data):
        self.followerA_pose = data # Store follower A
    def followerB_pose_cb(self, data):
        self.followerB_pose = data

    # Publish custom leader message: 0=Formation, 1=Return
    def publish_leader_message(self, instruction_id, message):
        msg = B00835055LeaderMessage()
        msg.instructionID = instruction_id
        msg.message = message
        msg.leader_x = self.pose.x
        msg.leader_y = self.pose.y
        msg.leader_theta = self.pose.theta
        msg.linear_velocity = self.pose.linear_velocity
        msg.angular_velocity = self.pose.angular_velocity
        msg.timestamp = rospy.get_time()
        self.leader_msg_pub.publish(msg)

    # Set pen colour for any turtle
    def set_pen(self, turtle_name, r, g, b, width, off):
        service_name = '/%s/set_pen' % turtle_name
        rospy.wait_for_service(service_name)
        pen = rospy.ServiceProxy(service_name, SetPen)
        pen(r, g, b, width, off)

    # CW1 Step 7: "All the turtles should return to their initial position with a white pen"
    def set_all_pens_white(self):
        self.set_pen(self.leader_name, 255, 255, 255, 2, 0)
        self.set_pen(self.followerA_name, 255, 255, 255, 2, 0)
        self.set_pen(self.followerB_name, 255, 255, 255, 2, 0)
        rospy.loginfo("All pens set to white")
    
    # Set coloured pens for formation movement
    def set_formation_pens(self):
        self.set_pen(self.leader_name, 255, 0, 0, 3, 0) # Red for leader
        self.set_pen(self.followerA_name, 0, 255, 0, 2, 0) # Green for followerA
        self.set_pen(self.followerB_name, 0, 0, 255, 2, 0) # Blue for followerB

    # Boundry detection
    def is_near_boundary(self):
        # Returns true if leader is close to any wall
        if self.pose is None:
            return False
        return (self.pose.x <= self.BOUNDARY_MIN or
                self.pose.x >= self.BOUNDARY_MAX or
                self.pose.y <= self.BOUNDARY_MIN or
                self.pose.y >= self.BOUNDARY_MAX)

    # Turning controller
    def turn_to_angle(self, target_angle):
        # Turn leader to face a specific angle using proportional control
        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            angle_diff = target_angle - self.pose.theta
            angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))
            if abs(angle_diff) < 0.05:
                self.vel_pub.publish(Twist())
                return
            vel_msg = Twist()
            vel_msg.angular.z = self.TURN_GAIN * angle_diff
            self.vel_pub.publish(vel_msg)
            rate.sleep()

    # Formation check
    def check_followers_in_formation(self):#
        # Check if both followers are within tolerance of their formation positions
        # CW1 Step 5: "Once the leader detects that the two followers are in the required formation position"
        # Formation: followerA 1m left, followerB 1m right of leader
        if self.followerA_pose is None or self.followerB_pose is None:
            return False

        # Calculate where followers SHOULD be in world coordinates
        # 1m to the left in the leader's frame = rotate by leader's theta
        # Left of leader: leader_pos + 1m at angle (theta + pi/2)
        targetA_x = self.pose.x + 1.0 * math.cos(self.pose.theta + math.pi / 2)
        targetA_y = self.pose.y + 1.0 * math.sin(self.pose.theta + math.pi / 2)

        # Right of leader: leader_pos + 1m at angle (theta - pi/2)
        targetB_x = self.pose.x + 1.0 * math.cos(self.pose.theta - math.pi / 2)
        targetB_y = self.pose.y + 1.0 * math.sin(self.pose.theta - math.pi / 2)

        # Distance to ideal position
        distA = math.sqrt((self.followerA_pose.x - targetA_x) ** 2 +
                          (self.followerA_pose.y - targetA_y) ** 2)
        distB = math.sqrt((self.followerB_pose.x - targetB_x) ** 2 +
                          (self.followerB_pose.y - targetB_y) ** 2)

        tolerance = 0.8 # Allow some tolerance
        return distA < tolerance and distB < tolerance

    # CW1 Step 7: "Teleport 2 followers to their initial position throughthe service (i.e. turtlesim/TeleportAbsolute) provided by ROS"
    def teleport_followers_to_initial(self):

        # Teleport follower A
        service_name = '/%s/teleport_absolute' % self.followerA_name
        rospy.wait_for_service(service_name)
        teleport = rospy.ServiceProxy(service_name, TeleportAbsolute)
        teleport(self.followerA_initial['x'],
                 self.followerA_initial['y'],
                 self.followerA_initial['theta'])
        rospy.loginfo("Teleported FollowerA to initial position (%.2f, %.2f)",
                      self.followerA_initial['x'], self.followerA_initial['y'])

        # Teleport follower B
        service_name = '/%s/teleport_absolute' % self.followerB_name
        rospy.wait_for_service(service_name)
        teleport = rospy.ServiceProxy(service_name, TeleportAbsolute)
        teleport(self.followerB_initial['x'],
                 self.followerB_initial['y'],
                 self.followerB_initial['theta'])
        rospy.loginfo("Teleported FollowerB to initial position (%.2f, %.2f)",
                      self.followerB_initial['x'], self.followerB_initial['y'])

    # CW1 Step 7:  "The leader turtle returns to the center through the custom service defined above 
                    (i.e. YourBcodeGoToTarget.srv). If the server fails to move the turtle to the goal location,
                    the leader turtle should be teleported back to the center"
    def leader_return_to_centre(self):
        rospy.loginfo("Leader returning to centre via GoToTarget service...")

        try:
            rospy.wait_for_service('go_to_target', timeout=5)
            go_to_target = rospy.ServiceProxy('go_to_target', B00835055GoToTarget)
            result = go_to_target(self.CENTRE_X, self.CENTRE_Y, 0.5, self.leader_name)

            if result.success:
                rospy.loginfo("Leader reached centre via service")
            else:
                rospy.logwarn("Service failed - teleporting leader to centre")
                self.teleport_leader_to_centre()
        except (rospy.ServiceException, rospy.ROSException) as e:
            rospy.logwarn("Service error: %s - teleporting leader to centre", e)
            self.teleport_leader_to_centre()

    # Fallback: teleport leader if service fails
    def teleport_leader_to_centre(self):
        service_name = '/%s/teleport_absolute' % self.leader_name
        rospy.wait_for_service(service_name)
        teleport = rospy.ServiceProxy(service_name, TeleportAbsolute)
        teleport(self.CENTRE_X, self.CENTRE_Y, 0.0)
        rospy.loginfo("Teleported leader to centre (%.3f, %.3f)", self.CENTRE_X, self.CENTRE_Y)

    # "CW1 Step 8: "clear the turtlesim screen"
    def clear_screen(self):
        rospy.wait_for_service('/clear')
        clear = rospy.ServiceProxy('/clear', Empty)
        clear()
        rospy.loginfo("Screen cleared")

    # Pick a random angle that points away from nearby walls
    def get_safe_random_angle(self):
        angle_min = -math.pi
        angle_max = math.pi

        if self.pose.x <= self.BOUNDARY_MIN + 0.5:
            angle_min = -math.pi / 2
            angle_max = math.pi / 2
        elif self.pose.x >= self.BOUNDARY_MAX - 0.5:
            angle_min = math.pi / 2
            angle_max = 3 * math.pi / 2

        if self.pose.y <= self.BOUNDARY_MIN + 0.5:
            angle_min = max(angle_min, 0.1)
            angle_max = min(angle_max, math.pi - 0.1)
        elif self.pose.y >= self.BOUNDARY_MAX - 0.5:
            angle_min = max(angle_min, -math.pi + 0.1)
            angle_max = min(angle_max, -0.1)

        return random.uniform(angle_min, angle_max)

    # Main cycle implementing CW1 Steps 4-8
    # Repeats: Formation -> Move -> Return -> Clear -> Repeat
    def run_cycle(self):

        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            # CW1 step 4: Send 'Formation' instruction
            rospy.loginfo("Sending Formation instruction")
            self.set_formation_pens()

            # Publish formation instruction repeatedly until followers arrive
            formation_timeout = 0
            while not rospy.is_shutdown() and not self.check_followers_in_formation():
                self.publish_leader_message(0, "Formation - move to position")
                formation_timeout += 1
                if formation_timeout > 300:  # 30 seconds timeout
                    rospy.logwarn("Formation timeout - proceeding anyway")
                    break
                rate.sleep()

            rospy.loginfo("Followers in formation (or timeout reached)")
            rospy.sleep(1)

            # CW1 step 5: Turn random direction and move straight
            rospy.loginfo("Leader moving with red pen")
            self.set_pen(self.leader_name, 255, 0, 0, 3, 0)  # Red pen

            random_angle = self.get_safe_random_angle()
            rospy.loginfo("Leader turning to angle: %.2f radians", random_angle)
            self.turn_to_angle(random_angle)

            # Nudge forward to escape boundary zone if needed
            nudge_count = 0
            while not rospy.is_shutdown() and self.is_near_boundary() and nudge_count < 20:
                vel_msg = Twist()
                vel_msg.linear.x = 1.5
                self.vel_pub.publish(vel_msg)
                self.publish_leader_message(0, "Formation mode - moving forward")
                nudge_count += 1
                rate.sleep()

            # Move forward until hitting boundary
            while not rospy.is_shutdown() and not self.is_near_boundary():
                vel_msg = Twist()
                vel_msg.linear.x = self.FORWARD_SPEED
                self.vel_pub.publish(vel_msg)
                self.publish_leader_message(0, "Formation mode - moving forward")
                rate.sleep()

            # Stop at boundary
            self.vel_pub.publish(Twist())
            self.boundary_hit_count += 1
            rospy.loginfo("Leader hit boundary #%d at (%.2f, %.2f)",
                          self.boundary_hit_count, self.pose.x, self.pose.y)

            # CW1 step 7: Send 'Return' instruction and reset
            rospy.loginfo("Return instruction - resetting")

            # Send Return instruction to followers
            for i in range(20):
                self.publish_leader_message(1, "Return - go to initial positions")
                rate.sleep()

            # Set all pens to white for the return journey
            # CW1 Spec: "All the turtles should return to their initial position with a white pen"
            self.set_all_pens_white()

            # Teleport followers to their initial positions
            # Spec: "Teleport 2 followers to their initial position through
            # the service (i.e. turtlesim/TeleportAbsolute)"
            self.teleport_followers_to_initial()

            # Leader returns to centre via the custom GoToTarget service
            # CW1 Spec: "The leader turtle returns to the center through the
            # custom service defined above"
            self.leader_return_to_centre()

            rospy.sleep(1)

            # CW1 step 8: Clear screen and repeat
            rospy.loginfo("=== STEP 8: Clearing screen, restarting cycle ===")
            self.clear_screen()
            rospy.sleep(1)

            # Loop back to Step 4

if __name__ == '__main__':
    try:
        LeaderNode()
    except rospy.ROSInterruptException:
        pass

#!/usr/bin/env python3

import rospy
import random
import math
from std_srvs.srv import Empty
from turtlesim.srv import Spawn, Kill, SetPen

def setup(): # Defining function
    rospy.init_node('setup_turtlesim')

    rospy.sleep(2) # Potential fix to loading, give time before calling its service
    
    # Set random background colour
    # Source:
    rospy.set_param('turtlesim/backgground_r', random.randint(0, 255))
    rospy.set_param('turtlesim/backgground_g', random.randint(0, 255))
    rospy.set_param('turtlesim/backgground_b', random.randint(0, 255))
    
    # Call '/cear' so turtlesim reads the parameters
    rospy.wait_for_service('/clear')
    clear = rospy.ServiceProxy('/clear', Empty)
    clear()
    rospy.loginfo("Background colour is set to random RGB values")
    
    # Kill the default turtle1
    # Source:
    rospy.wait_for_service('/kill')
    kill = rospy.ServiceProxy('/kill', Kill)
    try:
        kill('turtle1')
        rospy.loginfo("Killed default turtle1")
    except rospy.ServiceException as e:
        rospy.logwarn("Could not kill turtle1: %s", e)
    
    # Spawn the leader turtle
    # Source:
    rospy.wait_for_service('/spawn')
    spawn = rospy.ServiceProxy('/spawn', Spawn)
    
    leader_name = 'B00835055Leader'
    spawn(5.544, 5.544, 0.0, leader_name)
    rospy.loginfo("Spawned leader: %s at centre (5.544, 5.544)", leader_name)
    
    # Spawn 2 followers at random positions
    # Source:
    followerA_name = 'B00835055FollowerA'
    followerB_name = 'B00835055FollowerB'
    
    spawn(random.uniform(1.0, 10.0), # Random x axis
      random.uniform(1.0, 10.0), # Random y axis
      random.uniform(0, 2 * math.pi), # Random angle (0 to 2 pi radius)
      followerA_name)
    rospy.loginfo("Spawned follower: %s at random position", followerA_name)
    
    spawn(random.uniform(1.0, 10.0), # Random x axis
      random.uniform(1.0, 10.0), # Random y axis
      random.uniform(0, 2 * math.pi), # Random angle (0 to 2 pi radius)
      followerB_name)
    rospy.loginfo("Spawned follower: %s at random position", followerB_name)
    
    # Set leader's pen to red
    # W3 Lecture
    pen_service_name = '/%s/set_pen' % leader_name
    rospy.wait_for_service(pen_service_name)
    set_pen = rospy.ServiceProxy(pen_service_name, SetPen)
    set_pen(255, 0, 0, 3, 0) # r=255, g=0, b=3. off=0 (pen ON)
    rospy.loginfo("Set leader pen to red")
    
    # Set follower A pen to green
    pen_a_name = '/%s/set_pen' % followerA_name
    rospy.wait_for_service(pen_a_name)
    set_pen_a = rospy.ServiceProxy(pen_a_name, SetPen)
    set_pen_a(0, 255, 0, 2, 0)  # Green pen, width 2
    rospy.loginfo("Set follower A pen to green")

    # Set follower B pen to blue
    pen_b_name = '/%s/set_pen' % followerB_name
    rospy.wait_for_service(pen_b_name)
    set_pen_b = rospy.ServiceProxy(pen_b_name, SetPen)
    set_pen_b(0, 0, 255, 2, 0)  # Blue pen, width 2
    rospy.loginfo("Set follower B pen to blue")
    
if __name__ == '__main__':
    try:
        setup()
    except rospy.ROSInterruptException:
        pass

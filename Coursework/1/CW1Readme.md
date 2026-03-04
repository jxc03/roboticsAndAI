## Installing ROS Noetic 

1. Download/Install Oracle VirtualBox
2. Create VM 
3. Install Ubuntu LTS & Ubuntu <br>
3a. https://www.dotlinux.net/blog/how-to-fix-user-not-in-sudoers-file-error/ <br>
3b. sudo apt update <br>
3c. sudo apt upgrade <br>
3d. sudo apt install build-essential <br>
4. Click Devices, Insert guest Addition CD image or do it 
5. In Windows, create c:\ubuntu folder
6. In VirtualBox, Machine, Settings, Shared Folders, click the + button <br>
6a. Folder path, Other, browse to c:\ubuntu <br>
6b. Tick AutoMount and Make Permanent boxes <br>
7. https://wiki.ros.org/noetic/Installation/Ubuntu

## Setting Up Workspace

1. Create catkin workspace through the terminal on Ubuntu VM
```
# Create directory
mkdir -p ~/com760_ws/src 

# Go to directory
cd ~/com760_ws 

catkin_make # For building code in catkin, standard layout
```
2. Source setup / Make sure workspace is properly "overlayed"
```
# Source workspace but needs to be done EVERY time a new terminal is opened
source devel/setup.bash 

# For it to happen automatically
echo "source devel/setup.bash" >> ~/.bashrc
```
3. Create CW1 package
```
# Change directory to src
cd ~/com760_ws/src

# Create package 
catkin_create_pkg com760cw1_b00835055 rospy std_msgs geometry_msgs turtlesim message_generation message_runtime tf
```
4. Create folder structure
```
# Change directory 
cd com760cw1_b0083505560

# Create the required directories
mkdir -p launch scripts msg srv
```
5. Build everything to make sure it's working
```
# Build and re-source
~/com760_ws # Get to this directory .../
catkin_make
source devel/setup.bash

# Verify
rospack find com760cw1_b00835055

# Package structure should look like this:
com760cw1_b00835055/
├── package.xml
├── CMakeLists.txt
├── launch/          # launch files go here
├── scripts/         # Python nodes go here
├── msg/             # custom message definitions
└── srv/             # custom service definitions
```

## Setting Up Git & Github

1. Config git with details
```
git config --global user.name "Name"
git config --global user.email "Email Address"
```
2. Initialise git
```
cd ~/com760_ws/src/com760cw1_b00835055 # Get to this directory

# Initialise the repo
git init

# Create a .gitignore to not commit build artifacts
cat > .gitignore << 'EOF'

# Catkin build artifacts
build/
devel/
logs/
*.pyc
__pycache__/
.catkin_workspace

# IDE files
.vscode/
.idea/
*.swp
*~
EOF

# Stage everything
git add .

# First commit
git commit -m "Adding Git"

# Had to clone the repo, copy the workspace to the folder, fill username and password

# Push
git push
```

## The first script and launch file

1. Create script file
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055/scripts 

# Create Python file
gedit setup_turtlesim.py

# Code
import rospy
import random
import math
from std_srvs.srv import Empty
from turtlesim.srv import Spawn, Kill, SetPen

def setup():
    rospy.init_node('setup_turtlesim')

    rospy.set_param('/turtlesim/background_r', random.randint(0, 255))
    rospy.set_param('/turtlesim/background_g', random.randint(0, 255))
    rospy.set_param('/turtlesim/background_b', random.randint(0, 255))

    rospy.wait_for_service('/clear')
    clear = rospy.ServiceProxy('/clear', Empty)
    clear()
    rospy.loginfo("Background colour set to random RGB values")

    rospy.wait_for_service('/kill')
    kill = rospy.ServiceProxy('/kill', Kill)
    try:
        kill('turtle1')
        rospy.loginfo("Killed default turtle1")
    except rospy.ServiceException as e:
        rospy.logwarn("Could not kill turtle1: %s", e)

    rospy.wait_for_service('/spawn')
    spawn = rospy.ServiceProxy('/spawn', Spawn)

    leader_name = 'B00835055Leader'
    spawn(5.544, 5.544, 0.0, leader_name)
    rospy.loginfo("Spawned leader: %s at centre (5.544, 5.544)", leader_name)

    followerA_name = 'B00835055FollowerA'
    followerB_name = 'B00835055FollowerB'

    spawn(
        random.uniform(1.0, 10.0),       
        random.uniform(1.0, 10.0),        
        random.uniform(0, 2 * math.pi),     
        followerA_name
    )
    rospy.loginfo("Spawned follower: %s at random position", followerA_name)

    spawn(
        random.uniform(1.0, 10.0),
        random.uniform(1.0, 10.0),
        random.uniform(0, 2 * math.pi),
        followerB_name
    )
    rospy.loginfo("Spawned follower: %s at random position", followerB_name)

    pen_service_name = '/%s/set_pen' % leader_name
    rospy.wait_for_service(pen_service_name)
    set_pen = rospy.ServiceProxy(pen_service_name, SetPen)
    set_pen(255, 0, 0, 3, 0)  # r=255, g=0, b=0, width=3, off=0 (pen ON)
    rospy.loginfo("Set leader pen to red")
    
    # Part of enhancement:
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
```
- To edit file `nano FILENAME.launch`
- Make it executable by `chmod +x setup_turtlesim.py`
- Leader = red trail, follower A = green trail, follower B = blue trail

3. Create launch file
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055/launch

# Create launch file
gedit setup.launch

# Code
<launch>
    <!-- Launch the turtlesim simulator first -->
    <node pkg="turtlesim" type="turtlesim_node" name="turtlesim"/>

    <!-- Run our setup script (kills turtle1, spawns leader + followers) -->
    <node pkg="com760cw1_b00835055" type="setup_turtlesim.py" 
          name="setup_turtlesim" output="screen"/>
</launch>

# Build and test
cd ~/com760_ws
catkin_make
source devel/setup.bash
roslaunch com760cw1_b00835055 setup.launch

```
- `roslaunch` starts automatically if it's not already running, 3 turtles should appear
- Ensure indentation is 4, check for green spaces on `nano`

#£ Custom Messages, Services & The Proportional Controller

1. Create the custom message
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055/msg

# Create launch file
gedit B00835055LeaderMessage.msg

# Inside file:
int64 instructionID
string message

# Enhancing aftwerwards: 
float64 leader_x
float64 leader_y
float64 leader_theta
float64 linear_velocity
float64 angular_velocity
float64 timestamp
```
- `int64 instructionID` - An integer that tells followers what to do
- `string message` -  A description of the current instruction, useful for debugging and logging
- `leader_x`, `leader_y`, `leader_theta` - The leader's current position and heading. This gives followers a secondary way to know where the leader is
- `linear_velocity`, `angular_velocity` - How fast the leader is currently moving. Followers can use this to predict where the leader will be next therefor making their tracking smoother
- `timestamp` - When this message was sent. Useful for followers to check if the data is stale
- Instruction IDs:
    - 0, Formation = follow me, leader moving forward normally
    - 1, Turning - hold position, leader hit boundary & changing direction
    - 2, Stop - all halt, leader has stopped
    - 3, Return - go to start, command followers to return to their spawn positions
2. Create the custom service
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055/srv

# Create launch file
gedit B00835055GoToTarget.srv

# Inside file:
float32 goal_x
float32 goal_y
float32 tolerance
string turtle_name
---
bool success
# Enhancing aftwerwards: 
string status_message
float32 final_distance

```
- `---` - Everything above is the Request (what the client sends) and below is the Response (what the server sends back).
- `float32 goal_x` - target x coordinate on the turtlesim grid (0 to 11)
- `float32 goal_y` - target y coordinate
- `float32 tolerance` - how close the turtle needs to get before considering it "arrived" (e.g. 0.5 units)
- `string turtle_name` - which turtle to move (e.g. "B00835055FollowerA")
- `bool success` - `True` if the turtle reached the goal, `False` if it couldn't (e.g. goal was outside the grid)
- `status_message` - explanation like "Reached goal" or "Goal out of bounds" or "Timeout". More informative than just true/false.
- `final_distance` - how close the turtle actually got to the goal. Useful for debugging and shows the marker
3. Configure CMakeLists.txt
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055

# Edit file
gedit CMakeLists.txt

# Add/Replace 
add_message_files(
  FILES
  B00835055LeaderMessage.msg
)

# Add/Replace 
add_service_files(
  FILES
  B00835055GoToTarget.srv
)

# Add/Replace
generate_messages(DEPENDENCIES
  geometry_msgs  std_msgs
)

# Add/Replace
catkin_package(
  CATKIN_DEPENDS rospy std_msgs geometry_msgs turtlesim tf message_runtime
)
```
- `add_message_files` - Based from W3Lecture, generates services in the `msg` folder
- `add_service_files` - Based from W3Lecture, generates services in the `srv` folder
- `generate_messages` - Based from W3Lecture, generates added messages and services with any dependencies
- `catkin_package` - Based from W3Lecture, macro generates cmake config files for your package, 
4. Configure/Check package.xml
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055

# Edit file
gedit package.xml

# Check or Add:
<build_depend>message_generation</build_depend>
<exec_depend>message_runtime</exec_depend>
```
- `add_message_files` - Based from W3Lecture, generates services in the `msg` folder 
- 
5. Write the Go-To-Target Service Node
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055/scripts

# Create file
go_to_target_service.py

# Add in file:
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
            # Part of enhancing:
            rospy.logwarn("Goal out of bounds!")
            return B00835055GoToTargetResponse(
                success=False,
                status_message="Goal (%.2f, %.2f) is outside turtlesim bounds (0-11)" % (goal_x, goal_y),
                final_distance=-1.0
            )

            # rospy.logwarn("Goal (%.2f, %.2f) is outside turtlesim bounds!", goal_x, goal_y)
            # return B00835055GoToTargetResponse(False)

        # Subscribe to this turtle's pose topic
        # Each turtle has its own /turtleName/pose topic
        rospy.Subscriber('/%s/pose' % turtle_name, Pose,
                         self.pose_callback, turtle_name)

        # Create a publisher for this turtle's velocity commands
        pub = rospy.Publisher('/%s/cmd_vel' % turtle_name, Twist, queue_size=10)

        # Wait until the first pose is received
        rate = rospy.Rate(10)
        timeout_counter = 0 # Part of enhancing
        while turtle_name not in self.poses and not rospy.is_shutdown():
            # Part of enhancing:
            timeout_counter += 1
            if timeout_counter > 50: # 5 seconds at 10Hz
                return B00835055GoToTargetResponse(
                    success=False,
                    status_message="Timeout: Could not get pose for %s" % turtle_name,
                    final_distance=-1.0
                )
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
        # Part of enhancing:
        MAX_SPEED = 3.0
        MAX_ITERATIONS = 2000  # Safety limit to prevent infinite loops

        while not rospy.is_shutdown():
            pose = self.poses[turtle_name]

            # Calculate distance to goal (Euclidean distance)
            distance = math.sqrt((goal_x - pose.x) ** 2 + (goal_y - pose.y) ** 2)

            # Check if close enough
            if distance < tolerance:
                # Stop the turtle

                #Part of enhancing:
                rospy.loginfo("%s reached goal! Final distance: %.4f", turtle_name, distance)
                return B00835055GoToTargetResponse(
                    success=True,
                    status_message="Reached goal (%.2f, %.2f) successfully" % (goal_x, goal_y),
                    final_distance=distance
                )

                pub.publish(Twist())
                # rospy.loginfo("%s reached goal (%.2f, %.2f)!", turtle_name, goal_x, goal_y)
                # return B00835055GoToTargetResponse(True)

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
            vel_msg.linear.x = min(Kv * distance, MAX_SPEED) # Part of ehancing

            # vel_msg.linear.x = Kv * distance # Move faster whem far away

            vel_msg.angular.z = Kh * angle_diff # Rotate proportionally to angle error

            # Clamp linear speed to prevent the turtle going too fast
            # vel_msg.linear.x = min(vel_msg.linear.x, 3.0)
	    
	    # Publish velocity command
            pub.publish(vel_msg)
            iterations += 1 # Part of enhancing
            rate.sleep()

        # Part of enhancing   
        # If, Will time out    
        pub.publish(Twist())
        final_dist = math.sqrt(
            (goal_x - self.poses[turtle_name].x) ** 2 +
            (goal_y - self.poses[turtle_name].y) ** 2)
        return B00835055GoToTargetResponse(
            success=False,
            status_message="Timeout after %d iterations. Final distance: %.2f" % (iterations, final_dist),
            final_distance=final_dist
        )


if __name__ == '__main__':
    try:
        GoToTargetService()
    except rospy.ROSInterruptException:
        pass
```
- This is the proportional controller wrapped in a service, it's how turtles navigate to positions
- Explaination of proportional controller (Source: W2Lecture):
    - You're standing in a field and someone tells you to walk to a flag. You instinctively do two things: you turn to face the flag and you walk towards it. As you get closer, you slow down so you don't overshoot. That's exactly what the proportional controller does.
- Explaination of maths:
    - Step 1, where should I face - `θ* = atan2(y* - y, x* - x)`. This calculates the angle from the turtle's current position (x, y) to the goal (x*, y*). `atan2` is used instead of `atan` because `atan2` correctly handles all four quadrants; it knows the difference between "goal is ahead-left" and "goal is behind-right. Source W4Lecture
    - Step 2, How fast should I move forward - `v = Kv × √((x* - x)² + (y* - y)²)`. Linear speed is proportional to the distance to the goal. Far away = move fast. Close = move slowly. `Kv` is the gain constant that controls how aggressive this is.
    - Step 3, How fast should I turn - `ω = Kh × (θ* - θ)`. Angular speed is proportional to the angle error - the difference between where the turtle is facing (0) and where it should face (θ*). Big angle difference = turn quickly. Almost facing the right way = turn gently. `Kh` is the angular gain constant.
- Make script executable (goes from white to green) - chmod +x go_to_target_service.py
- New features:
    - Timeout protection - both for waiting for the pose (5 seconds) and for the navigation loop (2000 iterations). This prevents infinite loops if something goes wrong
    - Detailed status messages - the response tells you exactly what happened, not just true/false
    - Final distance reporting - even on failure, you know how close the turtle got
    - Speed clamping - `min(Kv * distance, MAX_SPEED)` prevents the turtle going unrealistically fast when far from the goal
6. Write the Leader Node
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055/scripts

# Create file
gedit leader_node.py

# Add in file:
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

        # Part of enhancing: Movement parameters
        self.FORWARD_SPEED = 2.0
        self.TURN_GAIN = 6.0

        # Boundary limits (turtlesim is ~11x11, stay away from edges)
        self.BOUNDARY_MIN = 0.5
        self.BOUNDARY_MAX = 10.5

        # Track how many boundary hits (for logging/vodcast)
        self.boundary_hit_count = 0

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
    # 0 = Formation mode, 1 = Return / Boundary hit
    def publish_leader_message(self, instruction_id, message):
        msg = B00835055LeaderMessage()
        msg.instructionID = instruction_id
        msg.message = message
        # Part of enhancing:
        msg.leader_x = self.pose.x
        msg.leader_y = self.pose.y
        msg.leader_theta = self.pose.theta
        msg.linear_velocity = self.pose.linear_velocity
        msg.angular_velocity = self.pose.angular_velocity
        msg.timestamp = rospy.get_time()
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
        # Kh = 6.0 # Angular gain

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
            vel_msg.angular.z = self.TURN_GAIN * angle_diff
            self.vel_pub.publish(vel_msg)

            # Part of enhancing: Publish turning instruction while rotating
            self.publish_leader_message(1, "Turning to new direction")
            rate.sleep()

    # Part of enhancing
    # Pick a random angle that points AWAY from the nearest wall
    # This prevents the leader from immediately hitting the same wall again after turning
    # Additional feature: smarter direction selection.        
    def get_safe_random_angle(self):

        # Determine which walls are close
        angle_min = -math.pi
        angle_max = math.pi

        if self.pose.x <= self.BOUNDARY_MIN + 0.5:
            # Near left wall - face right (angle between -pi/2 and pi/2)
            angle_min = -math.pi / 2
            angle_max = math.pi / 2
        elif self.pose.x >= self.BOUNDARY_MAX - 0.5:
            # Near right wall - face left
            angle_min = math.pi / 2
            angle_max = 3 * math.pi / 2

        if self.pose.y <= self.BOUNDARY_MIN + 0.5:
            # Near bottom wall - face upward
            angle_min = max(angle_min, 0.1)
            angle_max = min(angle_max, math.pi - 0.1)
        elif self.pose.y >= self.BOUNDARY_MAX - 0.5:
            # Near top wall - face downward
            angle_min = max(angle_min, -math.pi + 0.1)
            angle_max = min(angle_max, -0.1)

        return random.uniform(angle_min, angle_max)
             
    # Main loop: turn to random direction, move forward until boundary then repeat.
    # Source: W4 Practical Part A
    def run(self):
        rate = rospy.Rate(10)

        while not rospy.is_shutdown():
            # Phase 1: Turn to a random direction
            random_angle = self.get_safe_random_angle() # Part of enhancing
            rospy.loginfo("Leader turning to angle: %.2f radians", random_angle)
            # self.publish_leader_message(0, "Turning to new direction")
            self.turn_to_angle(random_angle)

            # Phase 2: Move forward until hitting boundary
            rospy.loginfo("Leader moving forward in formation mode")
            self.publish_leader_message(0, "Formation mode - moving forward")

            while not rospy.is_shutdown() and not self.is_near_boundary():
                vel_msg = Twist()
                # vel_msg.linear.x = 2.0 # Forward speed
                vel_msg.linear.x = self.FORWARD_SPEED # Part of enhancing
                self.vel_pub.publish(vel_msg)

                # Keep publishing the leader message so followers know the state
                self.publish_leader_message(0, "Formation mode - moving forward")
                rate.sleep()

            # Phase 3: Hit boundary, stop and notify
            self.vel_pub.publish(Twist()) # Stop movement
            # Part of enhancing
            self.boundary_hit_count += 1
            rospy.loginfo("Leader hit boundary #%d at (%.2f, %.2f)",
                          self.boundary_hit_count, self.pose.x, self.pose.y)

            # rospy.loginfo("Leader hit boundary at (%.2f, %.2f)",
                          self.pose.x, self.pose.y)
            # self.publish_leader_message(1, "Hit boundary - changing direction")

            # Part of enhancing: Publish stop instruction (ID=2) briefly             
            self.publish_leader_message(2, "Stopped at boundry")
            rospy.sleep(0.5) # Brief pause before turning again

            # Part of enhancing: Then publish turning instruction (ID=1)
	        self.publish_leader_message(1, "Changing direction after boundary hit")
	        rospy.sleep(0.5)

if __name__ == '__main__':
    try:
        LeaderNode()
    except rospy.ROSInterruptException:
        pass
```
- The leader runs in a continuous loop with three phases:
    - Phase 1: it picks a random angle between -π and π (any direction) and turns to face that way using the proportional controller for angular velocity
    - Phase 2: it moves straight forward at constant speed, continuously publishing the custom `B00835055LeaderMessage` with `instructionID=0` (formation mode). It also monitors its own position via the pose subscriber
    - Phase 3: when it detects it's near a boundary (x or y less than 0.5 or greater than 10.5), it stops, publishes instructionID=1 (return/change direction), pauses briefly then loops back to Phase 1 to pick a new random direction
- Make script executable (goes from white to green - ls ) - chmod +x leader_node.py
- New:
    - `get_safe_random_angle()` - Instead of picking a completely random direction (which might point straight back into the wall), this method picks an angle that points away from the nearest boundary. This is an additional feature
    - `boundary_hit_count` - Tracks how many times the leader has bounced off walls. Useful for logging
    - All four instruction IDs are used (0=Formation, 1=Turning, 2=Stop)
    - The full pose data is published in every message via the enhanced fields
7. Update the Launch File
```
# Go to directory
cd ~/com760_ws/src/com760cw1_b00835055/launch

# Edit file
gedit setup.launch

# Update file:
<launch>
    <!-- Launch the turtlesim simulator -->
    <node pkg="turtlesim" type="turtlesim_node" name="turtlesim"/>

    <!-- Setup: random background, kill turtle1, spawn leader + followers -->
    <node pkg="com760cw1_b00835055" type="setup_turtlesim.py"
          name="setup_turtlesim" output="screen"/>

    <!-- Go-to-target navigation service -->
    <node pkg="com760cw1_b00835055" type="go_to_target_service.py"
          name="go_to_target_service" output="screen"
          launch-prefix="bash -c 'sleep 5; $0 $@'"/>

    <!-- Leader control node -->
    <node pkg="com760cw1_b00835055" type="leader_node.py"
          name="leader_node" output="screen"
          launch-prefix="bash -c 'sleep 6; $0 $@'"/>
</launch>            
```
- The `launch-prefix="bash -c 'sleep 5; $0 $@'"` trick delays those nodes so the setup script finishes first (spawning turtles) before the leader tries to move   

## Fix the Leader boundary bug
1. Edit leader_note.py
```
# In leader_node.py
# Add following code before Phase 2:
            # Fix bug where leader gets stuck at the edge
            # Nudge forward to escape the boundry zone
            nudge_count = 0
            while not rospy.is_shutdown() and self.is_near_boundary() and nudge_count < 20:
                vel_msg = Twist()
                vel_msg.linear.x = 1.5
                self.vel_pub.publish(vel_msg)
                self.publish_leader_message(1, "Escaping boundary zone")
                nudge_count += 1
                rate.sleep()     
```
- The issue is that after turning, the leader is still inside the boundary zone so `is_near_boundary()` immediately returns true and it won't move forward. Adding a "nudge" after turning moves the forward for up to 20 ticks (2 seconds) to escape the boundary zone before starting the main forward movement loop

## tf Transforms & Follower Nodes (Formation Control)

- tf (transform) system: Every turtle's position in the simulator is in "world coordinates" (x, y on the 11×11 grid). The tf system lets each turtle broadcast its position as a named coordinate frame. Then any other node can listen and ask "where is the leader frame relative to the follower frame?" - tf handles all the maths automatically. Source: W4Lecture
- The carrot frame trick is key to formation control. Instead of making followers chase the leader directly (which would make them stack on top of each other), invisible "carrot" frames are created that are offset from the leader; one to the left, one to the right. Each follower chases its own carrot, creating a V-formation. Source: W4Lecture
- What is needed:
    - `turtle_tf_broadcaster.py`, broadcasts each turtle's pose as a tf frame
    - `carrot_frame_broadcaster.py`, creates offset "carrot" frames for formation
    - `follower_node.py`, uses tf listener to chase carrot frames
    - Update `setup.launch` - launch everything automatically

1. The tf Boradcaster
```
# In scripts folder, create turtle_tf_broadcaster.py
# cd then gedit FILENAME.py

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
```
- Subscribes to a turtle's /pose topic and broadcasts its position as a tf frame. It's parameterised so it can be reused for every turtle by passing a different turtle name
- Every time the turtlesim publishes a turtle's pose (which happens ~62 times per second), the callback converts that (x, y, theta) into a tf transform and broadcasts it. This creates a coordinate frame named after the turtle, positioned relative to the "world" frame
- In 2D, the turtle only rotates around the Z-axis (yaw). A quaternion is how ROS stores 3D rotations internally; it's a 4-number representation (x, y, z, w) that avoids gimbal lock issues. The function quaternion_from_euler(roll, pitch, yaw) does the conversion. Since turtlesim is 2D; roll and pitch are always 0. Source: W4Lecture

2. The Carriot Frame Broadcaster
```
# In scripts folder, create carrot_frame_broadcaster.py
# cd then gedit FILENAME.py

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
```

- Example if the leader is facing right and moving. The carrot frames are positioned 2 units behind and 1.5 units to each side. This creates a V-formation
- As the leader turns, the carrot frames rotate with it because they're children of the leader's frame in the tf tree. The followers automatically adjust their positions to maintain the V-shape. This is the core principle of leader-follower formation control
- If to change the formation shape (triangle, line, diamond), you'd just change the x and y offsets

3. The Follower Node
```
#!/usr/bin/env python3

# Uses tf2 listener to track the assigned carrot frame and navigate towards it. Responds to leader instructions (Formation/Return).

# References:
# - W4 Lecture Slide 24: "Writing a tf2 listener in Python"
# - W4 Lecture Slide 26: "The Proportional Controller" with tf
# - W4 Lecture Slide 47: "Adding a frame to tf2" (follower chases carrot)
# - CW1 Spec Steps 4-7

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
```

- Makes followers chase their  carrot frames using the tf listener and proportional controller


## Fix / Change Leader Note For Correct CW1
```
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
```

## Create / Update Launch file suited for CW1
```
<launch>
    <!-- Launch turtlesim simulator -->
    <node pkg="turtlesim" type="turtlesim_node" name="turtlesim"/>

    <!-- Setup: random background, spawn leader + followers -->
    <node pkg="com760cw1_b00835055" type="setup_turtlesim.py"
          name="setup_turtlesim" output="screen"/>

    <!-- tf broadcasters for each turtle -->
    <node pkg="com760cw1_b00835055" type="turtle_tf_broadcaster.py"
          name="leader_tf_broadcaster" output="screen"
          launch-prefix="bash -c 'sleep 4; $0 $@'">
        <param name="turtle_name" value="B00835055Leader"/>
    </node>

    <node pkg="com760cw1_b00835055" type="turtle_tf_broadcaster.py"
          name="followerA_tf_broadcaster" output="screen"
          launch-prefix="bash -c 'sleep 4; $0 $@'">
        <param name="turtle_name" value="B00835055FollowerA"/>
    </node>

    <node pkg="com760cw1_b00835055" type="turtle_tf_broadcaster.py"
          name="followerB_tf_broadcaster" output="screen"
          launch-prefix="bash -c 'sleep 4; $0 $@'">
        <param name="turtle_name" value="B00835055FollowerB"/>
    </node>

    <!-- Carrot frame broadcaster, formation offsets -->
    <node pkg="com760cw1_b00835055" type="carrot_frame_broadcaster.py"
          name="carrot_broadcaster" output="screen"
          launch-prefix="bash -c 'sleep 5; $0 $@'"/>

    <!-- Go-to-target navigation service -->
    <node pkg="com760cw1_b00835055" type="go_to_target_service.py"
          name="go_to_target_service" output="screen"
          launch-prefix="bash -c 'sleep 5; $0 $@'"/>

    <!-- Leader control node -->
    <node pkg="com760cw1_b00835055" type="leader_node.py"
          name="leader_node" output="screen"
          launch-prefix="bash -c 'sleep 7; $0 $@'">
        <param name="leader_name" value="B00835055Leader"/>
    </node>

    <!-- Follower nodes -->
    <node pkg="com760cw1_b00835055" type="follower_node.py"
          name="followerA_node" output="screen"
          launch-prefix="bash -c 'sleep 7; $0 $@'">
        <param name="follower_name" value="B00835055FollowerA"/>
        <param name="carrot_frame" value="carrot_followerA"/>
    </node>

    <node pkg="com760cw1_b00835055" type="follower_node.py"
          name="followerB_node" output="screen"
          launch-prefix="bash -c 'sleep 7; $0 $@'">
        <param name="follower_name" value="B00835055FollowerB"/>
        <param name="carrot_frame" value="carrot_followerB"/>
    </node>
</launch>
```
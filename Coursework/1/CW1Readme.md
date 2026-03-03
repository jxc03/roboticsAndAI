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
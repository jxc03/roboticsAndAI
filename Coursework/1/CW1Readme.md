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
cd com760cw1_b0083505560cd 

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

if __name__ == '__main__':
    try:
        setup()
    except rospy.ROSInterruptException:
        pass
```
- To edit file `nano FILENAME.launch`
- Make it executable by `chmod +x setup_turtlesim.py`
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
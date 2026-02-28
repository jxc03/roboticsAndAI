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
4. Build everything to make sure it's working
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

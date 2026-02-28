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
mkdir -p ~/com760_ws/src # Create directory
cd ~/com760_ws # Go to directory
catkin_make # For building code in catkin, standard layout
```

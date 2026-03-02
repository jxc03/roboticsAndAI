# Starting Turtlesim & Exploring ROS

## Terminal 1 - Start the ROS Master 
```
roscore
```

- ROS Master is like a phone directory - when a node starts, it registers with the master and when it needs to talk to another node, it asks the master how to find it. Every ROS system needs exactly one master running.
- The output ending should be along the line of "started core service [/rosout]" which means it's ready.
- If any errors during `roscore`, enter `roswtf`.
- To fix error with "local network configuration is invalid":

```
export ROS_IP=IP_ADDRESS
export ROS_MASTER_URI=http:IP_ADDRESS:11311

```

## Terminal 2 - Start the Turtlesim Simulator
```
rosrun turtlesim turtlesim_node
```

- The `rosrun` command takes 2 arguments: the package (`turtlesim`) and the node `turtlesim_node`.
- The node registered itself with the master and created a simulator window. The turtle starts at position (5.544, 5.544) which is the centre of the 11×11 unit grid. The origin (0,0) is at the bottom-left corner.
- A window pop up with a turtle in the centre.

## Terminal 3 - Exploring the system (To finish)
```
rosnode list

Output: 
/rosout
/turtlesim
```

- The `/rosout` is a logging node. /`turtlesim` is the simulator. Forward slash (`/`) before each name is the ROS convention.

# Moving the Turtle & Understanding Communication

## Terminal 4 - Keyboard control
```
rosrun turtlesim turtle_teleop_key
```

- To visualise the ROS graph:
```
rqt_graph
```

1. How many active nodes? 
From `rqt_graph` there are 2 active nodes relavant to the turtle: `/teleop_turtle` and `turtlesim`
2. What is the relationship between the two nodes? 
`/teleop_turtle` is a publisher and `turtlesim` is a subscriber. When arrow key is pressed, teleop_turtle creates `Twist` message and publishes it to `turtle1/cmd_vel` topic. The turtlesim node is subscribed to that topic, receives the message and moves the turtle accordingly. They don't talk directly - they communicate through the topic.
3. How is the turtle moved? Which topic is used?
The turtle is moved by publishing `geometry_msgs/Twist` messages to the `/turtle1/cmd_vel` topic. "cmd_vel" stands for "command velocity."

## Terminal 5 - Making the Turtle turn in a circle from the Command Line
```
1st way:
rostopic pub -r 1 /turtle1/cmd_vel geometry_msgs/Twist \
'{linear: {x: 2.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.8}}'

2nd way (Yaml style):

```
- `-r 10` publishes at 1 Hz
- linear.x controls forward speed, angular.z controls turning rate. If both are non-zero = circle
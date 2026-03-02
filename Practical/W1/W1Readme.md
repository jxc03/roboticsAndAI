# Starting Turtlesim & Exploring ROS

## Terminal 1 - Start the ROS Master 
```
roscore
```

- ROS Master is like a phone directory - when a node starts, it registers with the master and when it needs to talk to another node, it asks the master how to find it. Every ROS system needs exactly one master running.
- The output ending should be along the line of "started core service [/rosout]" which means it's ready.
- If any errors during 'roscore', enter 'roswtf'.
- To fix error with "local network configuration is invalid":
```
export ROS_IP=IP_ADDRESS
export ROS_MASTER_URI=http:IP_ADDRESS:11311

```
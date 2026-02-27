# traj_bringup

Bringup package for the trajectory tracking system. Provides launch files that orchestrate `trajectory_generator`, `pure_pursuit_tracker`, and (optionally) `red_rover_sim`.

All topics are namespaced under a configurable `robot_name` (default: `$ROVER_NAME` env var, falling back to `RR03`).

## Dependencies

Requires all three sibling packages in the same workspace:

- [trajectory_generator](https://github.com/kotakondo/trajectory_generator)
- [pure_pursuit_tracker](https://github.com/kotakondo/pure_pursuit_tracker)
- [red_rover_sim](https://github.com/kotakondo/red_rover_sim) (simulation only)

## Setup

```bash
mkdir -p ~/trajectory_generator_ws/src && cd ~/trajectory_generator_ws/src
git clone git@github.com:kotakondo/traj_bringup.git
git clone git@github.com:kotakondo/trajectory_generator.git
git clone git@github.com:kotakondo/pure_pursuit_tracker.git
git clone git@github.com:kotakondo/red_rover_sim.git  # simulation only
```

## Build

```bash
cd ~/trajectory_generator_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## Run

### Simulation (Gazebo + RViz + pure pursuit)

```bash
# Figure-8
ros2 launch traj_bringup full_system.launch.py traj_shape:=8

# Circle
ros2 launch traj_bringup full_system.launch.py traj_shape:=circle

# Line (back-and-forth)
ros2 launch traj_bringup full_system.launch.py traj_shape:=line

# Headless (no RViz)
ros2 launch traj_bringup full_system.launch.py traj_shape:=8 use_rviz:=false
```

### Hardware (no simulation)

Expects the hardware driver to provide `/<robot_name>/odom` (`nav_msgs/msg/Odometry`) and `odom`->`base_link` TF, and subscribe to `/<robot_name>/cmd_vel_auto` (`geometry_msgs/msg/Twist`).

```bash
# Figure-8
ros2 launch traj_bringup hardware.launch.py traj_shape:=8

# Circle
ros2 launch traj_bringup hardware.launch.py traj_shape:=circle

# Line
ros2 launch traj_bringup hardware.launch.py traj_shape:=line
```

### Launch arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `traj_shape` | (required) | Trajectory shape: `8`, `circle`, or `line` |
| `robot_name` | `$ROVER_NAME` or `RR03` | Namespace for all topics |
| `cmd_vel_topic` | `cmd_vel` (sim) / `cmd_vel_auto` (hw) | Output velocity command topic |
| `odom_topic` | `odom` | Input odometry topic |
| `use_rviz` | `true` | Launch RViz (simulation only) |

### Topic remapping examples

```bash
# Custom robot name
ros2 launch traj_bringup hardware.launch.py traj_shape:=8 robot_name:=ROVER1

# Custom odom and cmd_vel topics
ros2 launch traj_bringup hardware.launch.py traj_shape:=8 odom_topic:=odom_filtered cmd_vel_topic:=drive_cmd
```

## Verification

```bash
# Check topics, nodes, TF, and data flow (default namespace RR03)
bash src/traj_bringup/scripts/verify_system.sh

# Custom namespace
bash src/traj_bringup/scripts/verify_system.sh ROVER1
```

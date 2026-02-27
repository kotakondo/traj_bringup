#!/usr/bin/env python3
"""Launch tmux session for dynamic obstacle experiments.

Layout:
    +------------------------------------------+
    |               htop (top half)             |
    +--------+--------+---------+--------------------+
    | traj   | livox  |static_tf|       dlio         |
    | bringup|        |         |     (wider)        |
    +--------+--------+---------+--------------------+

Usage:
    python3 launch_dynamic_obstacle.py
"""

import subprocess
import sys
import time

SESSION = "docker_hardware_ground_robot"
WINDOW = "main"

SRC_COMMON = "source /opt/ros/humble/setup.bash && source /home/swarm/.bashrc"
SRC_MIGHTY = f"{SRC_COMMON} && source /home/swarm/code/mighty_ws/install/setup.bash"
SRC_TRAJ = f"{SRC_COMMON} && source /home/swarm/code/trajectory_generator_ws/install/setup.bash"


def tmux(*args):
    """Run a tmux command."""
    subprocess.run(["tmux"] + list(args), check=True)


def send_keys(pane, cmd, enter=True):
    """Send keys to a specific pane."""
    target = f"{SESSION}:{WINDOW}.{pane}"
    if enter:
        tmux("send-keys", "-t", target, cmd, "Enter")
    else:
        tmux("send-keys", "-t", target, cmd)


def main():
    # Kill existing session if it exists
    subprocess.run(
        ["tmux", "kill-session", "-t", SESSION],
        capture_output=True,
    )

    # Create session with first pane (will become htop - top half)
    tmux("new-session", "-d", "-s", SESSION, "-n", WINDOW)

    # Split into top (50%) and bottom (50%)
    tmux("split-window", "-v", "-t", f"{SESSION}:{WINDOW}.0", "-p", "50")

    # Split bottom row into 4 panes: traj(7%) | livox(7%) | static_tf(6%) | dlio(80%)
    tmux("split-window", "-h", "-t", f"{SESSION}:{WINDOW}.1", "-p", "93")
    tmux("split-window", "-h", "-t", f"{SESSION}:{WINDOW}.2", "-p", "93")
    tmux("split-window", "-h", "-t", f"{SESSION}:{WINDOW}.3", "-p", "92")

    # Pane 0: htop (top half, full width)
    send_keys(0, "htop")

    # Pane 1: Traj bringup - source workspace, type command without executing
    send_keys(1, SRC_TRAJ)
    time.sleep(2)
    send_keys(
        1,
        "ros2 launch traj_bringup hardware.launch.py traj_shape:=line",
        enter=False,
    )

    # Pane 2: Livox
    send_keys(2, SRC_MIGHTY)
    send_keys(
        2, "ros2 launch livox_ros_driver2 run_MID360_launch.py namespace:=$ROVER_NAME"
    )

    # Pane 3: Static TF
    send_keys(3, SRC_MIGHTY)
    send_keys(
        3,
        "ros2 run tf2_ros static_transform_publisher 0 0 0 0 0.3490659 0 "
        "$ROVER_NAME/base_link $ROVER_NAME/lidar",
    )

    # Pane 4: DLIO (rightmost, wider pane ~50%)
    send_keys(4, SRC_MIGHTY)
    send_keys(
        4,
        "ros2 launch direct_lidar_inertial_odometry dlio.launch.py namespace:=$ROVER_NAME",
    )

    # Attach to session
    if sys.stdout.isatty():
        tmux("attach-session", "-t", SESSION)
    else:
        print(f"Session '{SESSION}' created. Attach with: tmux attach -t {SESSION}")


if __name__ == "__main__":
    main()

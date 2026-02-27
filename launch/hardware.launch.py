"""
Hardware launch file — trajectory generator + pure pursuit tracker (no simulation).

Expects the hardware driver to provide:
  - /<robot_name>/<odom_topic>        (nav_msgs/msg/Odometry)
  - /tf                               (odom → base_link)

And to subscribe to:
  - /<robot_name>/<cmd_vel_topic>     (geometry_msgs/msg/Twist)

Usage:
  ros2 launch traj_bringup hardware.launch.py traj_shape:=8
  ros2 launch traj_bringup hardware.launch.py traj_shape:=circle robot_name:=ROVER1
  ros2 launch traj_bringup hardware.launch.py traj_shape:=8 odom_topic:=odom_filtered cmd_vel_topic:=drive_cmd
"""

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
    LogInfo,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    traj_shape_arg = DeclareLaunchArgument(
        "traj_shape",
        description='traj_shape should be set to either 8, circle, or line',
        choices=["8", "circle", "line"],
    )

    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value=EnvironmentVariable('ROVER_NAME', default_value='RR03'),
        description="Robot namespace for all topics",
    )

    odom_topic_arg = DeclareLaunchArgument(
        "odom_topic", default_value="odom",
        description="Input odometry topic name (relative to namespace)",
    )

    cmd_vel_topic_arg = DeclareLaunchArgument(
        "cmd_vel_topic", default_value="cmd_vel_auto",
        description="Output velocity command topic name (relative to namespace)",
    )

    # 1. Trajectory generator (immediate — no Gazebo to wait for)
    traj = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("trajectory_generator"),
                    "launch",
                    "trajectory_generator.launch.py",
                ]
            )
        ),
        launch_arguments={
            "traj_shape": LaunchConfiguration("traj_shape"),
            "robot_name": LaunchConfiguration("robot_name"),
        }.items(),
    )

    # 2. Pure pursuit tracker (delayed 2s to let trajectory publish)
    pursuit = TimerAction(
        period=2.0,
        actions=[
            LogInfo(msg="Launching pure pursuit tracker..."),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution(
                        [
                            FindPackageShare("pure_pursuit_tracker"),
                            "launch",
                            "pure_pursuit.launch.py",
                        ]
                    )
                ),
                launch_arguments={
                    "robot_name": LaunchConfiguration("robot_name"),
                    "odom_topic": LaunchConfiguration("odom_topic"),
                    "cmd_vel_topic": LaunchConfiguration("cmd_vel_topic"),
                }.items(),
            ),
        ],
    )

    return LaunchDescription([
        traj_shape_arg, robot_name_arg, odom_topic_arg, cmd_vel_topic_arg,
        traj, pursuit,
    ])

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

    use_rviz = DeclareLaunchArgument(
        "use_rviz",
        default_value="true",
        description="Launch RViz for visualization",
    )

    robot_name_arg = DeclareLaunchArgument(
        "robot_name",
        default_value=EnvironmentVariable('ROVER_NAME', default_value='RR03'),
        description="Robot namespace for all topics",
    )

    # 1. Simulation (Gazebo + robot_state_publisher + spawn)
    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("red_rover_sim"), "launch", "simulation.launch.py"]
            )
        ),
        launch_arguments={
            "use_rviz": LaunchConfiguration("use_rviz"),
            "robot_name": LaunchConfiguration("robot_name"),
        }.items(),
    )

    # 2. Trajectory generator (delayed 5s to let Gazebo start)
    traj = TimerAction(
        period=5.0,
        actions=[
            LogInfo(msg="Launching trajectory generator..."),
            IncludeLaunchDescription(
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
            ),
        ],
    )

    # 3. Pure pursuit tracker (delayed 7s to let trajectory publish)
    pursuit = TimerAction(
        period=7.0,
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
                }.items(),
            ),
        ],
    )

    return LaunchDescription([traj_shape_arg, use_rviz, robot_name_arg, sim, traj, pursuit])

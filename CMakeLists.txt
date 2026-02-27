cmake_minimum_required(VERSION 3.8)
project(traj_bringup)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch scripts config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()

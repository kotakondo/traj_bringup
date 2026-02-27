#!/bin/bash
ROBOT_NAME="${1:-RR03}"
echo "=== SYSTEM VERIFICATION (namespace: ${ROBOT_NAME}) ==="
echo ""
echo "--- Topics ---"
ros2 topic list | grep -E "cmd_vel|odom|trajectory|markers|lookahead"
echo ""
echo "--- Nodes ---"
ros2 node list
echo ""
echo "--- TF ---"
timeout 3 ros2 run tf2_ros tf2_echo odom base_link 2>&1 | head -5
echo ""
echo "--- Data Flow ---"
echo "Reference trajectory:"
timeout 5 ros2 topic echo /${ROBOT_NAME}/reference_trajectory --once 2>&1 | head -10
echo ""
echo "Odometry:"
timeout 5 ros2 topic echo /${ROBOT_NAME}/odom --once 2>&1 | head -5
echo ""
echo "Cmd vel:"
timeout 5 ros2 topic echo /${ROBOT_NAME}/cmd_vel --once 2>&1 | head -5
echo ""
echo "Actual trajectory:"
timeout 5 ros2 topic echo /${ROBOT_NAME}/actual_trajectory --once 2>&1 | head -5
echo ""
echo "=== VERIFICATION COMPLETE ==="

# Copyright (c) 2019 Boston Dynamics, Inc.  All rights reserved.
#
# Downloading, reproducing, distributing or otherwise using the SDK Software
# is subject to the terms and conditions of the Boston Dynamics Software
# Development Kit License (20191101-BDSDK-SL).

"""Tests for the robot command client."""

from bosdyn.client.robot_command import (_robot_command_error, _robot_command_feedback_error,
                                         _clear_behavior_fault_error, RobotCommandBuilder)

from bosdyn.api import robot_command_pb2
from bosdyn.api import geometry_pb2
from bosdyn.api import robot_command_pb2

from bosdyn.client import ResponseError, InternalServerError, LeaseUseError, UnsetStatusError


def test_robot_command_error():
    # Test unset header error
    response = robot_command_pb2.RobotCommandResponse()
    assert isinstance(_robot_command_error(response), UnsetStatusError)
    # Test header error
    response.header.error.code = response.header.error.CODE_INTERNAL_SERVER_ERROR
    assert isinstance(_robot_command_error(response), InternalServerError)
    # Test lease use error
    response.header.error.code = response.header.error.CODE_OK
    response.lease_use_result.status = response.lease_use_result.STATUS_INVALID_LEASE
    assert isinstance(_robot_command_error(response), LeaseUseError)
    # Test unset status error
    response.lease_use_result.status = response.lease_use_result.STATUS_OK
    assert isinstance(_robot_command_error(response), UnsetStatusError)
    # Test status error
    response.status = response.STATUS_UNSUPPORTED
    assert isinstance(_robot_command_error(response), ResponseError)
    # Test OK
    response.status = response.STATUS_OK
    assert not _robot_command_error(response)


def test_robot_command_feedback_error():
    # Test unset header error
    response = robot_command_pb2.RobotCommandFeedbackResponse()
    assert isinstance(_robot_command_feedback_error(response), UnsetStatusError)
    # Test header error
    response.header.error.code = response.header.error.CODE_INTERNAL_SERVER_ERROR
    assert isinstance(_robot_command_feedback_error(response), InternalServerError)
    # Test unset status error
    response.header.error.code = response.header.error.CODE_OK
    assert isinstance(_robot_command_feedback_error(response), UnsetStatusError)
    # Test status error
    response.status = response.STATUS_COMMAND_OVERRIDDEN
    assert isinstance(_robot_command_feedback_error(response), ResponseError)
    # Test OK
    response.status = response.STATUS_PROCESSING
    assert not _robot_command_feedback_error(response)


def test_behavior_fault_clear_error():
    # Test unset header error
    response = robot_command_pb2.ClearBehaviorFaultResponse()
    assert isinstance(_clear_behavior_fault_error(response), UnsetStatusError)
    # Test header error
    response.header.error.code = response.header.error.CODE_INTERNAL_SERVER_ERROR
    assert isinstance(_clear_behavior_fault_error(response), InternalServerError)
    # Test lease use error
    response.header.error.code = response.header.error.CODE_OK
    response.lease_use_result.status = response.lease_use_result.STATUS_INVALID_LEASE
    assert isinstance(_clear_behavior_fault_error(response), LeaseUseError)
    # Test unset status error
    response.lease_use_result.status = response.lease_use_result.STATUS_OK
    assert isinstance(_clear_behavior_fault_error(response), UnsetStatusError)
    # Test status error
    response.status = response.STATUS_NOT_CLEARED
    assert isinstance(_clear_behavior_fault_error(response), ResponseError)
    # Test OK
    response.status = response.STATUS_CLEARED
    assert not _clear_behavior_fault_error(response)


def _test_has_full_body(command):
    assert isinstance(command, robot_command_pb2.RobotCommand)
    assert command.HasField("full_body_command")
    assert not command.HasField("mobility_command")


def _test_has_mobility(command):
    assert isinstance(command, robot_command_pb2.RobotCommand)
    assert command.HasField("mobility_command")
    assert not command.HasField("full_body_command")


def test_stop_command():
    command = RobotCommandBuilder.stop_command()
    _test_has_full_body(command)
    assert command.full_body_command.HasField("stop_request")


def test_freeze_command():
    command = RobotCommandBuilder.freeze_command()
    _test_has_full_body(command)
    assert command.full_body_command.HasField("freeze_request")


def test_selfright_command():
    command = RobotCommandBuilder.selfright_command()
    _test_has_full_body(command)
    assert command.full_body_command.HasField("selfright_request")


def test_safe_power_off_command():
    command = RobotCommandBuilder.safe_power_off_command()
    _test_has_full_body(command)
    assert command.full_body_command.HasField("safe_power_off_request")


def test_trajectory_command():
    goal_x = 1.0
    goal_y = 2.0
    goal_heading = 3.0
    frame = geometry_pb2.Frame(base_frame=geometry_pb2.FRAME_KO)
    command = RobotCommandBuilder.trajectory_command(goal_x, goal_y, goal_heading, frame)
    _test_has_mobility(command)
    assert command.mobility_command.HasField("se2_trajectory_request")
    traj = command.mobility_command.se2_trajectory_request.trajectory
    assert len(traj.points) == 1
    assert traj.points[0].pose.position.x == goal_x
    assert traj.points[0].pose.position.y == goal_y
    assert traj.points[0].pose.angle == goal_heading
    assert traj.frame == frame


def test_velocity_command():
    v_x = 1.0
    v_y = 2.0
    v_rot = 3.0
    command = RobotCommandBuilder.velocity_command(v_x, v_y, v_rot)
    _test_has_mobility(command)
    assert command.mobility_command.HasField("se2_velocity_request")
    vel_cmd = command.mobility_command.se2_velocity_request
    assert vel_cmd.velocity.linear.x == v_x
    assert vel_cmd.velocity.linear.y == v_y
    assert vel_cmd.velocity.angular == v_rot
    assert vel_cmd.frame.base_frame == geometry_pb2.FRAME_BODY


def test_stand_command():
    command = RobotCommandBuilder.stand_command()
    _test_has_mobility(command)
    assert command.mobility_command.HasField("stand_request")


def test_sit_command():
    command = RobotCommandBuilder.sit_command()
    _test_has_mobility(command)
    assert command.mobility_command.HasField("sit_request")

# -*- coding: utf-8 -*-

# Software License Agreement (BSD License)
#
# Copyright (c) 2014, TORK (Tokyo Opensource Robotics Kyokai Association)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of TORK. nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import time

from hironx_ros_bridge.hironx_client import HIRONX


class AcceptanceTest_Hiro():
    '''
    This class holds methods that can be used for verification of the robot
    Kawada Industries' dual-arm robot Hiro (and the same model of other robots
    e.g. NEXTAGE OPEN).

    This test class is:
    - Intended to be run as nosetests, ie. roscore isn't available by itself.
    - Almost all the testcases don't run without an access to a robot running.

    Above said, combined with a rostest that launches roscore and robot (either
    simulation or real) hopefully these testcases can be run, both in batch
    manner by rostest and in nosetest manner.

    Prefix for methods 'at' means 'acceptance test'.
    
    All time arguments are second.
    '''

    def init(self, robotname='HiroNX(Robot)0', url=''):
        self.robot = hiro = HIRONX()
        self.robot.init(robotname=args.robot, url=args.modelfile)

    def run_tests_ros(self):
        '''
        Run by ROS exactly the same actions that run_tests_hrpsys performs. 
        '''
        True

    def run_tests_hrpsys(self):
        _TIME_SETTARGETP_L = 3
        _TIME_SETTARGETP_R = 2
        _TIME_BW_TESTS = 5

        self.robot.goInitial()

        # === TASK-1 === 
        # L arm setTargetPose
        _POS_L_INIT = self.robot.getCurrentPosition('LARM_JOINT5')
        _POS_L_INIT[2] += 0.8
        _RPY_L_INIT = self.robot.getCurrentRPY('LARM_JOINT5')
        self.robot.setTargetPose('larm', _POS_L_INIT, _RPY_L_INIT, _TIME_SETTARGETP_L)
        self.robot.waitInterpolationOfGroup('larm')

        # R arm setTargetPose
        _POS_R_INIT = self.robot.getCurrentPosition('RARM_JOINT5')
        _POS_R_INIT[2] -= 0.07
        _RPY_R_INIT = self.robot.getCurrentRPY('RARM_JOINT5')
        self.robot.setTargetPose('rarm', _POS_R_INIT, _RPY_R_INIT, _TIME_SETTARGETP_R)
        self.robot.waitInterpolationOfGroup('rarm')
        time.sleep(_TIME_BW_TESTS)

        # === TASK-2 === 
        self.robot.goInitial()
        # Both arm setTargetPose
        _Z_SETTARGETP_L = 0.08
        _Z_SETTARGETP_R = 0.08
        self.robot.setTargetPoseRelative('larm', 'LARM_JOINT5',
                                         dz=_Z_SETTARGETP_L,
                                         tm=_TIME_SETTARGETP_L, wait=False)
        self.robot.setTargetPoseRelative('rarm', 'RARM_JOINT5',
                                         dz=_Z_SETTARGETP_R,
                                         tm=_TIME_SETTARGETP_R, wait=False)

        # === TASK-3 === 
        # Head toward down
        _TIME_HEAD = 5
        self.robot.setTargetPoseRelative('head', 'HEAD_JOINT0', dp=0.1, tm=_TIME_HEAD)
        self.robot.waitInterpolationOfGroup('head')
        # Head toward up
        self.robot.setTargetPoseRelative('head', 'HEAD_JOINT0', dp=-0.2, tm=_TIME_HEAD)
        self.robot.waitInterpolationOfGroup('head')
        # See left by position
        self.robot.setJointAnglesOfGroup('head', [50, 10], 2, wait=True)
        # See right by position
        self.robot.setJointAnglesOfGroup('head', [-50, -10], 2, wait=True)
        # Set back face to the starting pose w/o wait. 
        self.robot.setJointAnglesOfGroup( 'head', [0, 0], 2, wait=False)

        # === TASK-4 === 
        # 0.1mm increment is not working for some reason.
        self.robot.goInitial()
        # Move by iterating 0.1mm at cartesian space
        _TIME_CARTESIAN = 0.1
        _INCREMENT_MIN=0.0001
        for i in range(300):
            self.robot.setTargetPoseRelative('larm', 'LARM_JOINT5',
                                             dy=_INCREMENT_MIN,
                                             tm=_TIME_CARTESIAN)
            self.robot.setTargetPoseRelative('rarm', 'RARM_JOINT5',
                                             dy=_INCREMENT_MIN,
                                             tm=_TIME_CARTESIAN)
            print('{}th move'.format(i))

        self.robot.goInitial()
        # === TASK-5 === 
        # Turn torso
        _TORSO_ANGLE = 120
        _TIME_TORSO_R = 7
        self.robot.setJointAnglesOfGroup('torso', [_TORSO_ANGLE], _TIME_TORSO_R, wait=True)
        self.robot.waitInterpolationOfGroup('torso')
        self.robot.setJointAnglesOfGroup('torso', [-_TORSO_ANGLE], 10, wait=True)
 
        self.robot.goInitial()

        # === TASK-6.1 === 
        # Overwrite previous command, for torso using setJointAnglesOfGroup
        self.robot.setJointAnglesOfGroup('torso', [_TORSO_ANGLE], _TIME_TORSO_R, wait=False)
        time.sleep(1)
        self.robot.setJointAnglesOfGroup('torso', [-_TORSO_ANGLE], 10, wait=True)

        self.robot.goInitial(5)

        # === TASK-6.2 === 
        # Overwrite previous command, for arms using setTargetPose
        _X_EEF_OVERWRITE = 0.05
        _Z_EEF_OVERWRITE = 0.1
        _TIME_EEF_OVERWRITE = 7
        _POS_L_INIT[0] += _X_EEF_OVERWRITE
        _POS_L_INIT[2] += _Z_EEF_OVERWRITE
        self.robot.setTargetPose('larm', _POS_L_INIT, _RPY_L_INIT, _TIME_EEF_OVERWRITE)
        self.robot.waitInterpolationOfGroup('larm')
        # Trying to raise rarm to the same level of larm.
        _POS_R_INIT[0] += _X_EEF_OVERWRITE
        _POS_R_INIT[2] += _Z_EEF_OVERWRITE
        self.robot.setTargetPose('rarm', _POS_R_INIT, _RPY_R_INIT, _TIME_EEF_OVERWRITE)
        self.robot.waitInterpolationOfGroup('rarm')
        time.sleep(3)
        # Stop rarm
        self.robot.clearOfGroup('rarm')  # Movement should stop here.

        # === TASK-7.1 === 
        # Cover wide workspace.
        _TIME_COVER_WORKSPACE = 3
        # Close to the max width the robot can spread arms with the hand kept
        # at table level.
        _POS_L_X_NEAR_Y_FAR = [0.32552812002303166, 0.47428609880442024, 1.0376656470275407]
        _RPY_L_X_NEAR_Y_FAR = (-3.07491977663752, -1.5690249316560323, 3.074732073335767)
        _POS_R_X_NEAR_Y_FAR = [0.32556456455769633, -0.47239119592815987, 1.0476131608682244]
        _RPY_R_X_NEAR_Y_FAR = (3.072515432213872, -1.5690200270375372, -3.072326882451363)
        
        # Close to the farthest distance the robot can reach, with the hand kept
        # at table level.
        _POS_L_X_FAR_Y_FAR = [0.47548142379781055, 0.17430276793604782, 1.0376878025614884]
        _RPY_L_X_FAR_Y_FAR = (-3.075954857224205, -1.5690261926181046, 3.0757659493049574)
        _POS_R_X_FAR_Y_FAR = [0.4755337947019357, -0.17242322190721648, 1.0476395479774052]
        _RPY_R_X_FAR_Y_FAR = (3.0715850722714944, -1.5690204449882248, -3.071395243174742)
        self.robot.setTargetPose('larm', _POS_L_X_NEAR_Y_FAR, _RPY_L_X_NEAR_Y_FAR, _TIME_COVER_WORKSPACE)
        self.robot.setTargetPose('rarm', _POS_R_X_NEAR_Y_FAR, _RPY_R_X_NEAR_Y_FAR, _TIME_COVER_WORKSPACE)
        self.robot.waitInterpolationOfGroup('larm')
        self.robot.waitInterpolationOfGroup('rarm')
        time.sleep(3)
        self.robot.setTargetPose('larm', _POS_L_X_FAR_Y_FAR, _RPY_L_X_FAR_Y_FAR, _TIME_COVER_WORKSPACE)
        self.robot.setTargetPose('rarm', _POS_R_X_FAR_Y_FAR, _RPY_R_X_FAR_Y_FAR, _TIME_COVER_WORKSPACE)
        self.robot.waitInterpolationOfGroup('larm')
        self.robot.waitInterpolationOfGroup('rarm')

        self.robot.goInitial()

import argparse

from hrpsys import rtm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='hiro command line interpreters')
    parser.add_argument('--host', help='corba name server hostname')
    parser.add_argument('--port', help='corba name server port number')
    parser.add_argument('--modelfile', help='robot model file nmae')
    parser.add_argument('--robot', help='robot modlule name (RobotHardware0 for real robot, Robot()')
    args, unknown = parser.parse_known_args()

    if args.host:
        rtm.nshost = args.host
    if args.port:
        rtm.nsport = args.port
    if not args.robot:
        args.robot = 'RobotHardware0' if args.host else 'HiroNX(Robot)0'
    if not args.modelfile:
        args.modelfile = ''

    # support old style format
    if len(unknown) >= 2:
        args.robot = unknown[0]
        args.modelfile = unknown[1]
    acceptance_test = AcceptanceTest_Hiro()
    acceptance_test.init(robotname=args.robot, url=args.modelfile)

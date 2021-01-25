#!/usr/bin/env python
import tf_conversions
import numpy as np
import message_filters
import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
import time
import roslib; roslib.load_manifest('ur_driver')
roslib.load_manifest('robotic_origami')
import rospy
import actionlib
from std_msgs.msg import Int8
from ur_moveit_myplan.msg import qr_status
from apriltag_ros.msg import AprilTagDetection, AprilTagDetectionArray
from control_msgs.msg import *
from trajectory_msgs.msg import *
from sensor_msgs.msg import JointState
from math import sqrt, pi, acos, sin, cos
from moveit_msgs.msg import RobotTrajectory
from moveit_msgs.msg import *
from trajectory_msgs.msg import JointTrajectoryPoint
from geometry_msgs.msg import PoseStamped, Pose
from math import sqrt, pi, acos, sin, cos, atan2, tan
from std_msgs.msg import String,Empty,UInt16
import parameter_generation as pg
import tf
from arc_rotate import *

rospy.init_node('dual_arm_origami', anonymous=True)
moveit_commander.roscpp_initialize(sys.argv)

listener = tf.TransformListener()

robot = moveit_commander.RobotCommander()
scene = moveit_commander.PlanningSceneInterface()
rospy.sleep(2)
group_name1 = "hong_arm"
group1 = moveit_commander.MoveGroupCommander(group_name1)
group_name2 = "kong_arm"
group2 = moveit_commander.MoveGroupCommander(group_name2)
group_name3 = "hong_hand"
group3 = moveit_commander.MoveGroupCommander(group_name3)
group_name4 = "kong_hand"
group4 = moveit_commander.MoveGroupCommander(group_name4)
###set rigid gripper pose group.set_joint_value_target([1]) ---> group.go()
display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path',
                                               moveit_msgs.msg.DisplayTrajectory,
                                               queue_size=20)



global odom_c_pub
# diaplay center point
odom_c_pub = rospy.Publisher("/odom_c", Odometry, queue_size=50)

#global motion group
global display_trajectory_trigger_pub
display_trajectory_trigger_pub = rospy.Publisher(
                                      '/display_trigger',
                                      String,
                                      queue_size=20)

print "============  Start now"

def gripper_pose(angle,gripper_name):
##input angle in degree
    if gripper_name == "hong_hand":
        group = group3
    elif gripper_name == "kong_hand":
        group = group4
    else:
        print "robot_arm input error, please input valid robot_arm name"
    angle=angle*pi/180
    group.set_joint_value_target([angle])
    result=group.go()
    print "============ Gripper: %s target: %s " % (gripper_name, angle)
    print "============ result:%s" % result

def addCollisionObjects():
    global wall_pose1
    global wall_name1
    wall_pose1 = geometry_msgs.msg.PoseStamped()
    wall_pose1.header.frame_id = "world"
    wall_pose1.pose.orientation.w = 1.0
    wall_pose1.pose.orientation.x = 0
    wall_pose1.pose.orientation.y = 0
    wall_pose1.pose.orientation.z = 1
    wall_pose1.pose.position.x = -2.1
    wall_pose1.pose.position.y = 0.0
    wall_pose1.pose.position.z = 1.0
    wall_name1 = "wall1"
    global wall_pose2
    global wall_name2
    wall_pose2 = geometry_msgs.msg.PoseStamped()
    wall_pose2.header.frame_id = "world"
    wall_pose2.pose.orientation.w = 1.0
    wall_pose2.pose.orientation.x = 0
    wall_pose2.pose.orientation.y = 0
    wall_pose2.pose.orientation.z = 1
    wall_pose2.pose.position.x = 2.1
    wall_pose2.pose.position.y = 0.0
    wall_pose2.pose.position.z = 1.0
    wall_name2 = "wall2"

def robhong_go_to_home(state):
    if state == 1:
        joint_values = [-66.86/180*pi, -69.6/180*pi, -120.2/180*pi, -51.78/180*pi, 77.87/180*pi, 111.00/180*pi]
    elif state == 2:
        joint_values = []
    group1.set_joint_value_target(joint_values)
    plan = group1.plan()
    print "============ hong_home"
    rospy.sleep(2)
    scaled_traj2 = scale_trajectory_speed(plan, 0.5)
    group1.execute(scaled_traj2)

def robkong_go_to_home(state):
    if state == 1:
        joint_values = [45.80/180*pi, -108.10/180*pi, 111.35/180*pi, -113.3/180*pi, -72.05/180*pi, 47.2/180*pi]
    elif state == 2:
        joint_values = []
    group2.set_joint_value_target(joint_values)
    plan = group2.plan()
    print "============ kong_home"
    rospy.sleep(2)
    scaled_traj2 = scale_trajectory_speed(plan, 0.5)
    group2.execute(scaled_traj2)

def move_target(x, y, z, ox, oy, oz, ow, vel,robot_arm):
    if robot_arm == "robhong":
        group = group1
    elif robot_arm == "robkong":
        group = group2
    else:
        print "robot_arm input error, please input valid robot_arm name"
        return 0
    pose_target = geometry_msgs.msg.Pose()
    pose_target.orientation.x = ox
    pose_target.orientation.y = oy
    pose_target.orientation.z = oz
    pose_target.orientation.w = ow
    pose_target.position.x = x
    pose_target.position.y = y
    pose_target.position.z = z
    group.set_pose_target(pose_target)
    plan = group.plan()
    scaled_traj = scale_trajectory_speed(plan, vel)
    print "move_target"
    group.execute(scaled_traj)

def move_waypoints(dx,dy,dz,vel,robot_arm):
    if robot_arm == "robhong":
        group = group1
    elif robot_arm == "robkong":
        group = group2
    else:
        print "robot_arm input error, please input valid robot_arm name"
        return 0
    waypoints = []
    waypoints.append(group.get_current_pose().pose)
    wpose = copy.deepcopy(group.get_current_pose().pose)
    wpose.position.x += dx
    wpose.position.y += dy
    wpose.position.z += dz
    waypoints.append(copy.deepcopy(wpose))
    (plan, fraction) = group.compute_cartesian_path(waypoints, 0.02, 0.0)
    new_traj = scale_trajectory_speed(plan,vel)
    result=group.execute(new_traj)
    print "move waypoint result"
    print dx,dy,dz,robot_arm
    print result

def scale_trajectory_speed(traj, scale):
    new_traj = moveit_msgs.msg.RobotTrajectory()
    new_traj.joint_trajectory = traj.joint_trajectory
    n_joints = len(traj.joint_trajectory.joint_names)
    n_points = len(traj.joint_trajectory.points)
    points = list(traj.joint_trajectory.points)

    for i in range(n_points):
        point = trajectory_msgs.msg.JointTrajectoryPoint()
        point.time_from_start = traj.joint_trajectory.points[i].time_from_start / scale
        point.velocities = list(traj.joint_trajectory.points[i].velocities)
        point.accelerations = list(traj.joint_trajectory.points[i].accelerations)
        point.positions = traj.joint_trajectory.points[i].positions

        for j in range(n_joints):
            point.velocities[j] = point.velocities[j] * scale
            point.accelerations[j] = point.accelerations[j] * scale * scale
        points[i] = point

    new_traj.joint_trajectory.points = points
    return new_traj


def group_rotate_by_external_axis(center_point, axis, total_angle,robot_arm):
    global odom_c_pub
    if robot_arm == "robhong":
        group = group1
    elif robot_arm == "robkong":
        group = group2
    else:
        print "robot_arm input error, please input valid robot_arm name"
        return 0
    pose_target = group.get_current_pose().pose

    waypoints_new = calc_waypoints_ARC(pose_target, center_point, axis, total_angle, odom_c_pub)
    # Before the execution of the real robot, turn on the display of the end effector's position and orientation
    # display end effector's trajectory
    # subcriber of display_trajectory_trigger and corresponding function is implemented in 'display_markers.py'
    display_trajectory_trigger_pub.publish('on')
    rospy.sleep(1)

    # Utilize 'compute_cartesian_path' to get a smooth trajectory
    (plan3, fraction) = group.compute_cartesian_path(
                           waypoints_new,   # waypoints to follow
                           0.01,        # eef_step
                           0.0)         # jump_threshold

    # Move the robot with the ARC trajectory
    caled_plan = scale_trajectory_speed(plan3, 0.5)
    group.execute(caled_plan)
    rospy.sleep(1)

    # Stop displaying end effector's posision and orientation
    display_trajectory_trigger_pub.publish('close')


def move_along_axis(axis,dist,robot_arm):
    if robot_arm == "robhong":
        group = group1
    elif robot_arm == "robkong":
        group = group2
    else:
        print "robot_arm input error, please input valid robot_arm name"
    targ_x=axis[0]*dist
    targ_y=axis[1]*dist
    targ_z=axis[2]*dist
    move_waypoints(targ_x,targ_y,targ_z,0.35,robot_arm)

def descend_to_desktop(robot_arm,gripper_state,margin):
    if robot_arm == "robhong":
        group = group1
        pinch_tip='pinch_tip_hong'
    elif robot_arm == "robkong":
    group = group2
    pinch_tip='pinch_tip_kong'
    else:
        print "robot_arm input error, please input valid robot_arm name"

    current_z=group.get_current_pose().pose.position.z

    if gripper_state== "normal":
        target_z = 0.840+margin
        dz=target_z-current_z
    elif gripper_state=="pinch":
        target_z =0.704+margin
        listener.waitForTransform("world", pinch_tip, rospy.Time(), rospy.Duration(4.0))
        (trans_pinch,rot_) = listener.lookupTransform("world", pinch_tip, rospy.Time(0))
        dz=target_z-trans_pinch[2]
    elif gripper_state=="pinch2":
        target_z =0.702+margin
        dz=target_z-current_z
    else:
        print "wrong gripper state"

    move_waypoints(0,0,dz,0.4,robot_arm)
    rospy.sleep(3)
    print "=========== %s descend_to_desktop" % robot_arm


def fold(global_axis,degree,robot_arm):
    trans_soft=[]
    if robot_arm == "robhong":
        group = group1
        listener.waitForTransform("world", "pinch_tip_hong", rospy.Time(), rospy.Duration(4.0))
        (trans_soft,rot_) = listener.lookupTransform("world", "rigid_tip_hong", rospy.Time(0))
    elif robot_arm == "robkong":
        group = group2
        listener.waitForTransform("world", "pinch_tip_kong", rospy.Time(), rospy.Duration(4.0))
        (trans_soft,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))
    else:
        print "robot_arm input error, please input valid robot_arm name"
    return 0
    group_rotate_by_external_axis(trans_soft,global_axis,degree,robot_arm)

def fix(trans_fixed_tag,fix_rot_angle,robot_arm):
    if robot_arm == "robhong":
        rigid_tip="rigid_tip_hong"
        gripper_state=101
    elif robot_arm == "robkong":
        rigid_tip="rigid_tip_kong"
        gripper_state=201
    else:
        print "robot_arm input error, please input valid robot_arm name"
    ##############hong_arm to fix the object
    arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    rospy.sleep(1)
    arduino_pub.publish(gripper_state)

    listener.waitForTransform("world", rigid_tip, rospy.Time(), rospy.Duration(4.0))
    (trans_rigH,rot_) = listener.lookupTransform("world", rigid_tip, rospy.Time(0))
    trans_rig2tag = np.subtract(trans_fixed_tag,trans_rigH,).tolist()
    print "fixed trans_rig2tag"
    print trans_rig2tag

    phi=-30
    listener.waitForTransform("world", rigid_tip, rospy.Time(), rospy.Duration(4.0))
    (trans_rigH,rot_) = listener.lookupTransform("world", rigid_tip, rospy.Time(0))
    group_rotate_by_external_axis(trans_rigH, [0, 1, 0], phi,robot_arm)
    phi=fix_rot_angle
    listener.waitForTransform("world", rigid_tip, rospy.Time(), rospy.Duration(4.0))
    (trans_rigH,rot_) = listener.lookupTransform("world", rigid_tip, rospy.Time(0))
    group_rotate_by_external_axis(trans_rigH, [0, 0, 1], phi,robot_arm)

    #move to fixed tag
    listener.waitForTransform("world", rigid_tip, rospy.Time(), rospy.Duration(4.0))
    (trans_rigH,rot_) = listener.lookupTransform("world", rigid_tip, rospy.Time(0))
    trans_rig2tag= np.subtract(trans_fixed_tag,trans_rigH).tolist()
    move_waypoints(trans_rig2tag[0],trans_rig2tag[1],0.0,0.4,robot_arm)
    #arm descend

    descend_to_desktop(robot_arm,'normal',0.005)

    listener.waitForTransform("world", rigid_tip, rospy.Time(), rospy.Duration(4.0))
    (trans_rigH,rot_) = listener.lookupTransform("world", rigid_tip, rospy.Time(0))

    print "============ trans_rigH is %s" % trans_rigH

def flexflip(ref_tag,trans_target2ref,target_rot_angle,trans_fix2ref,fix_rot_angle,crease_axis,crease_perp_l,margin):
    ##IN CONVENTION: crease_axis and perp_axis have negative y axis value for tag 15 and tag 17
    ##               crease_axis and perp_axis have positive y axis value for tag 27 and tag 29

    if crease_axis[0]*crease_axis[1]>=0:
        sign=-1
    elif crease_axis[0]*crease_axis[1]<0:
        sign=1

    if crease_axis[1]>=0:
        ori=-1
    elif crease_axis[1]<0:
        ori=1

    z=[0,0,1]
    perp_axis=np.cross(z,crease_axis)  #perp_axis=[-0.7071,-0.7071,0]
    rot1_angle =15*sign                    #15
    rot2_angle=20*sign                     #20
    rot3_angle=-45*sign                      #-45
    rot4_angle=-34*sign                      #-25

    crease_perp_l=crease_perp_l*ori
    margin_x=-perp_axis[0]*margin[0]*sign
    margin_y=-perp_axis[1]*margin[1]*sign

    print "============ perp_axis is %s" % perp_axis
    ########## flexflip starts here
    print "============= Start felxflip"
    ############## init grippers
    arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    rospy.sleep(1)
    arduino_pub.publish(201)

    #####Obtain key info of tags
    listener.waitForTransform("world", ref_tag, rospy.Time(), rospy.Duration(4.0))
    (trans_ref,rot_) = listener.lookupTransform("world", ref_tag, rospy.Time(0))

    ##############kong_arm to initial pose
    phi=30
    listener.waitForTransform("world", "soft_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_soft,rot_) = listener.lookupTransform("world", "soft_tip_kong", rospy.Time(0))
    group_rotate_by_external_axis(trans_soft, [0, 1.0, 0], phi,"robkong")
    phi=target_rot_angle
    listener.waitForTransform("world", "soft_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_soft,rot_) = listener.lookupTransform("world", "soft_tip_kong", rospy.Time(0))
    group_rotate_by_external_axis(trans_soft, [0, 0, 1.0], phi,"robkong")

    listener.waitForTransform("world", "soft_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_soft,rot_) = listener.lookupTransform("world", "soft_tip_kong", rospy.Time(0))
    #move to top of target tag
    trans_target= np.add(trans_target2ref,trans_ref).tolist()
    trans_soft2targ = np.subtract(trans_target,trans_soft).tolist()
    trans_fix= np.add(trans_fix2ref,trans_ref).tolist()
    print "============ trans_ref is %s" % trans_ref
    print "============ trans_target is %s" % trans_target
    print "============ trans_fix is %s" % trans_fix




    move_waypoints(trans_soft2targ[0]+margin_x,trans_soft2targ[1]+margin_y,0.00,0.35,'robkong')
    #kong_arm descend
    descend_to_desktop('robkong','normal',0.004+margin[2])

    ###################################### start to fix the end via hong_arm/robhong/group1
    fix(trans_fix,fix_rot_angle,'robhong')

    ####################################### flex-flip and grasp
    arduino_pub.publish(202)
    rospy.sleep(4)

    move_waypoints(0,0,0.01,0.08,'robkong')
    rospy.sleep(1)
    listener.waitForTransform("world", "soft_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_soft,rot_) = listener.lookupTransform("world", "soft_tip_kong", rospy.Time(0))
    #rot1: to hold the paper after flexflip
    group_rotate_by_external_axis(trans_soft, crease_axis, rot1_angle,'robkong')
    #pinch!
    rospy.sleep(1)
    arduino_pub.publish(203)
    rospy.sleep(2)
    move_waypoints(0.0,0.0,0.01,0.3,'robkong')


    #rot2: make pinch tip vertical

    fold(crease_axis,rot2_angle,'robkong')

    listener.waitForTransform("world", "pinch_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))
    delta_z=-trans_pinch[2]+0.708+0.05
    move_waypoints(0,0,delta_z,0.02,'robkong')
    #rot3:rot pinch tip for crease
    fold(crease_axis,rot3_angle,'robkong')
    move_along_axis(perp_axis,-crease_perp_l,'robkong')

    listener.waitForTransform("world", "pinch_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))
    delta_z=-trans_pinch[2]+0.697
    move_waypoints(0,0,delta_z,0.03,'robkong')

    ####let arm fixing the paper go home
    robhong_go_to_home(1)
    #rot4: rot more to leave space for other robot arm
    fold(crease_axis,rot4_angle,'robkong')
    # grasp the paper tip tighter
    arduino_pub.publish(212)



def scoop_pinch(fixed_tag,fix_rot_angle,crease_axis,crease_perp_l,target2fix,scoop_angle):
    z=[0,0,1]
    normal_axis=np.cross(z,crease_axis)

    # set gripper to pinch state
    arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    rospy.sleep(3)
    arduino_pub.publish(1)
    rospy.sleep(2)
    arduino_pub.publish(221)
    rospy.sleep(2)

    if scoop_angle>0:
        sign=-1
    elif scoop_angle<0:
        sign=1

    ##### initialize
    listener.waitForTransform("world", fixed_tag, rospy.Time(), rospy.Duration(4.0))
    (trans_fixed_tag,rot_) = listener.lookupTransform("world", fixed_tag, rospy.Time(0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))

    trans_target_tag = [trans_fixed_tag[0]+target2fix[0],trans_fixed_tag[1]+target2fix[1],trans_fixed_tag[2]]
    #### fix the paper before scooping
    fix(trans_fixed_tag,fix_rot_angle,'robhong')
    ##############kong_arm to initial pose
    phi= scoop_angle
    group_rotate_by_external_axis(trans_pinch, [0, 0, 1.0], phi,"robkong")

    #move to top of target tag
    listener.waitForTransform("world", "pinch_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))

    trans_pinch2tag = np.subtract(trans_target_tag,trans_pinch).tolist()
    tag_dist=0.0282
    move_waypoints(trans_pinch2tag[0]+3.6*tag_dist,trans_pinch2tag[1],0,0.3,'robkong')
    #kong_arm descend
    descend_to_desktop('robkong','pinch2',0.11)

    ###### start scooping pinch
    # normal_axis=[0,1,0]
    ###################################offset_unit is the key parameter to tune
    offset_unit=0.07*sign
    pinch_dist=[normal_axis[0]*offset_unit,normal_axis[1]*offset_unit,normal_axis[2]*offset_unit]
    move_waypoints(pinch_dist[0],pinch_dist[1],0,0.2,'robkong')
    rospy.sleep(1)
    arduino_pub.publish(203)
    rospy.sleep(5)

def crease(trans_ref,pinch_z_angle,crease_axis,crease_length,startP2refP,z_axis,margin_z,margin_offset):

    ##IN CONVENTION: crease_axis and normal_axis have negative y axis value
    if crease_axis[1]>=0:
        ori=1
    elif crease_axis[1]<0:
        ori=1


    normal_axis=np.cross(z_axis,crease_axis)  #perp_axis=[-0.7071,-0.7071,0] default z_axis=[0,0,1]

    offset_unit=-(0.015+margin_offset)*ori
    shift_unit=0.02

    # make sure hong is at home
    robhong_go_to_home(1)
    # scoop uses single arm, currently hong_arm/robhong/group1
    print "============ Start scooping"
    # set gripper_hong's rigid finger to pinch state
    arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    rospy.sleep(1)
    arduino_pub.publish(121)

    ##############hong_arm to start pose
    listener.waitForTransform("world", "pinch_tip_hong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinchH,rot_) = listener.lookupTransform("world", "pinch_tip_hong", rospy.Time(0))


    phi=pinch_z_angle
    group_rotate_by_external_axis(trans_pinchH, [0, 0, 1], phi,"robhong")

    listener.waitForTransform("world", "pinch_tip_hong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinchH,rot_) = listener.lookupTransform("world", "pinch_tip_hong", rospy.Time(0))
    trans_pinch2tag = np.subtract(trans_ref,trans_pinchH).tolist()
    trans_pinch2start = np.add(startP2refP,trans_pinch2tag).tolist()
    #move to scooping x and y pose
    move_waypoints(trans_pinch2start[0],trans_pinch2start[1],0.0,0.35,'robhong')
    #hong_arm descend
    descend_to_desktop('robhong','pinch',margin_z)

    ##################  start to make a crease along defined axis
    pinch_dist=[normal_axis[0]*offset_unit,normal_axis[1]*offset_unit,normal_axis[2]*offset_unit]
    shift_dist=[crease_axis[0]*shift_unit,crease_axis[1]*shift_unit,crease_axis[2]*shift_unit]
    #liwei: add margin_unit and margin_dist
    margin_unit=0.0015*ori
    margin_dist=[normal_axis[0]*margin_unit,normal_axis[1]*margin_unit,normal_axis[2]*margin_unit]
    num_attempts=int(crease_length//shift_unit)
    print "====pinch attempts"
    print num_attempts
    for i in range(0,num_attempts):
        listener.waitForTransform("world", "pinch_tip_hong", rospy.Time(), rospy.Duration(4.0))
        (trans_pH,rot_) = listener.lookupTransform("world", "pinch_tip_hong", rospy.Time(0))
        (trans_pK,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))
        trans_delta=np.subtract(trans_pK,trans_pH).tolist()
        print "======== trans_pH", trans_pH
        print "======== trans_pK", trans_pK
        print "======== trans_delta", trans_delta
        dist=sqrt(trans_delta[0]**2+trans_delta[1]**2)
        print "======== dist between tips ", dist
        #liwei: change 0.024 to 0.03
        if dist>=0.03:
            move_waypoints(pinch_dist[0],pinch_dist[1],pinch_dist[2],0.2,"robhong")
            arduino_pub.publish(112)
            rospy.sleep(6)
            arduino_pub.publish(111)
            rospy.sleep(3)
            move_waypoints(-pinch_dist[0],-pinch_dist[1],-pinch_dist[2],0.2,"robhong")
            move_waypoints(margin_dist[0],margin_dist[1],margin_dist[2],0.2,"robhong")
        else:
            rospy.sleep(3)
        move_waypoints(shift_dist[0],shift_dist[1],shift_dist[2],0.2,"robhong")

    move_waypoints(pinch_dist[0],pinch_dist[1],pinch_dist[2],0.2,"robhong")
    arduino_pub.publish(112)
    rospy.sleep(6)
    arduino_pub.publish(111)
    rospy.sleep(2)

    move_waypoints(shift_dist[0],shift_dist[1],shift_dist[2],0.2,"robhong")


    robhong_go_to_home(1)

    arduino_pub.publish(211)
    rospy.sleep(3)
    move_waypoints(0,0,0.01,0.1,'robkong')
    move_waypoints(0,0.2,0.02,0.3,'robkong')
    robkong_go_to_home(1)

    arduino_pub.publish(1)
    rospy.sleep(2)

def scoop_fold(fixed_tag,fix_rot_angle,crease_axis,crease_perp_l,target2fix,scoop_angle,offset,tilt_angle):
    z=[0,0,1]
    normal_axis=np.cross(z,crease_axis)

    # set gripper to pinch state
    arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    rospy.sleep(3)
    arduino_pub.publish(1)
    rospy.sleep(3)
    arduino_pub.publish(221)
    rospy.sleep(2)

    if scoop_angle>0:
        sign=-1
    elif scoop_angle<0:
        sign=1

    ##### initialize
    listener.waitForTransform("world", fixed_tag, rospy.Time(), rospy.Duration(4.0))
    (trans_fixed_tag,rot_) = listener.lookupTransform("world", fixed_tag, rospy.Time(0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))

    trans_target_tag = [trans_fixed_tag[0]+target2fix[0],trans_fixed_tag[1]+target2fix[1],trans_fixed_tag[2]]
    #### fix the paper before scooping
    fix(trans_fixed_tag,fix_rot_angle,'robhong')
    ##############kong_arm to initial pose
    phi= scoop_angle
    group_rotate_by_external_axis(trans_pinch, [0, 0, 1.0], phi,"robkong")

    #move to top of target tag
    listener.waitForTransform("world", "pinch_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))

    trans_pinch2tag = np.subtract(trans_target_tag,trans_pinch).tolist()
    tag_dist=0.0282
    move_waypoints(trans_pinch2tag[0]+3.6*tag_dist,trans_pinch2tag[1],0,0.3,'robkong')
    #kong_arm descend
    descend_to_desktop('robkong','pinch2',0.11)

    ###### start scooping pinch
    # normal_axis=[0,1,0]
    ###################################offset_unit is the key parameter to tune
    offset_unit=offset*sign
    pinch_dist=[normal_axis[0]*offset_unit,normal_axis[1]*offset_unit,normal_axis[2]*offset_unit]
    move_waypoints(pinch_dist[0],pinch_dist[1],0,0.2,'robkong')
    rospy.sleep(1)
    arduino_pub.publish(203)
    rospy.sleep(5)

    ############################################ start folding
    move_waypoints(0,0,0.03,0.2,'robkong')
    degree=50
    global_axis=[1,0,0]
    center_point=[trans_target_tag[0],trans_target_tag[1]-0.12,trans_target_tag[2]]
    group_rotate_by_external_axis(center_point,global_axis,degree,'robkong')
    rospy.sleep(1)
    # move_waypoints(0,-0.01,0,0.2,'robkong')

    # move along crease
    listener.waitForTransform("world", "pinch_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))
    degree=-20
    global_axis=[1,0,0]
    center_point=trans_pinch
    group_rotate_by_external_axis(center_point,global_axis,degree,'robkong')

    offset_unit=crease_perp_l*sign
    pinch_dist=[normal_axis[0]*offset_unit,normal_axis[1]*offset_unit,normal_axis[2]*offset_unit]
    move_waypoints(pinch_dist[0],pinch_dist[1],0,0.2,'robkong')
    rospy.sleep(2)

    listener.waitForTransform("world", "pinch_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))
    delta_z=-trans_pinch[2]+0.712
    move_waypoints(0,0,delta_z,0.03,'robkong')

    # let hong go home
    robhong_go_to_home(1)

    # tilt more to fix the tag
    listener.waitForTransform("world", "pinch_tip_kong", rospy.Time(), rospy.Duration(4.0))
    (trans_pinch,rot_) = listener.lookupTransform("world", "pinch_tip_kong", rospy.Time(0))
    degree=tilt_angle
    global_axis=[1,0,0]
    center_point=trans_pinch
    group_rotate_by_external_axis(center_point,global_axis,degree,'robkong')



def turn_over(robot_arm,angle,margin):
    if robot_arm == "robhong":
        group = group1
        target="pinch_tip_hong"
        robkong_go_to_home(1)
    elif robot_arm == "robkong":
        group = group2
        target="pinch_tip_kong"
        robhong_go_to_home(1)
    else:
        print "robot_arm input error, please input valid robot_arm name"


    move_waypoints(0,0,0.3,0.35,robot_arm)
    rospy.sleep(1)

    listener.waitForTransform("world", target, rospy.Time(), rospy.Duration(4.0))
    (trans_pinchH,rot_) = listener.lookupTransform("world", target, rospy.Time(0))

    group_rotate_by_external_axis(trans_pinchH, [1, 0, 0], angle,robot_arm)

    descend_to_desktop(robot_arm,'pinch',margin)

    arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    rospy.sleep(3)
    arduino_pub.publish(211)
    rospy.sleep(1)
    arduino_pub.publish(111)


def test_frame_accuracy(robot_arm,ref_tag):

    if robot_arm == "robhong":
        group = group1
        soft_tip='soft_tip_hong'
        sign=-1
    elif robot_arm == "robkong":
        group = group2
        soft_tip='soft_tip_kong'
        sign=1
    else:
        print "robot_arm input error, please input valid robot_arm name"


    ########## flexflip starts here
    print "============= Start accuracy test"
    ############## init grippers
    arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    rospy.sleep(3)
    arduino_pub.publish(1)

    #####Obtain key info of tags
    listener.waitForTransform("world", ref_tag, rospy.Time(), rospy.Duration(4.0))
    (trans_ref,rot_) = listener.lookupTransform("world", ref_tag, rospy.Time(0))

    ##############kong_arm to initial pose
    phi=30*sign
    listener.waitForTransform("world", soft_tip, rospy.Time(), rospy.Duration(4.0))
    (trans_soft,rot_) = listener.lookupTransform("world", soft_tip, rospy.Time(0))
    group_rotate_by_external_axis(trans_soft, [0, 1.0, 0], phi, robot_arm)


    listener.waitForTransform("world", soft_tip, rospy.Time(), rospy.Duration(4.0))
    (trans_soft,rot_) = listener.lookupTransform("world", soft_tip, rospy.Time(0))
    #move to top of target tag
    trans_target= trans_ref
    trans_soft2targ = np.subtract(trans_target,trans_soft).tolist()
    print "============ trans_ref is %s" % trans_ref



    move_waypoints(trans_soft2targ[0],trans_soft2targ[1],0.00,0.35,robot_arm)

    #kong_arm descend
    descend_to_desktop(robot_arm,'normal',0.004)
    listener.waitForTransform("world", soft_tip, rospy.Time(), rospy.Duration(4.0))
    (trans_soft,rot_) = listener.lookupTransform("world", soft_tip, rospy.Time(0))
    print "============ result is %s" % trans_soft

#_____INITIALIZATION______#
# We can get the name of the reference frame for this robot:
def init():
    group1.clear_pose_targets()
    group2.clear_pose_targets()
    planning_frame = group1.get_planning_frame()
    print "============ Reference frame1: %s" % planning_frame
    planning_frame = group2.get_planning_frame()
    print "============ Reference frame2: %s" % planning_frame
    print "============ Robot Groups:", robot.get_group_names()

    robkong_go_to_home(1)
    robhong_go_to_home(1)

    arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    rospy.sleep(1)
    arduino_pub.publish(1)

### liwei: add wall after go to home
#   scene.add_box(wall_name1,wall_pose1,(2,0.04,2))
#   scene.add_box(wall_name2,wall_pose2,(2,0.04,2))


def transCentertoWorld(transTag2World,rotTag2World,transCenterTag2Tag,rotCenterTag2Tag):
    #transformation from planning center to world
    #input[0]:array; input[1]:array, matrix; input[2]:array; input[3]:array, matrix
    pos,rot = transCentertoTag(transCenterTag2Tag,rotCenterTag2Tag)
    rotCenter2World = np.dot(rotTag2World,rot)
    posCenter2World = transTag2World + np.dot(rotTag2World,pos)
    return posCenter2World,rotCenter2World

def get_tag_info(referenced_tag):
    ########get transformations
    listener.waitForTransform(reference_tag, "tag_22", rospy.Time(), rospy.Duration(4.0))
    (trans1,rot1)=listener.lookupTransform(reference_tag, 'tag_22', rospy.Time(0))
    # print "trans1",trans1
    rot_mat1=listener.fromTranslationRotation(trans1, rot1)
    rot_mat1 = rot_mat1[:3,:3]
    # print "rot1",rot_mat1
    trans,rot = transCentertoTag(trans1,rot_mat1)
    # listener.waitForTransform("world", reference_tag, rospy.Time(), rospy.Duration(4.0))
    # (trans2,rot2) = listener.lookupTransform("world", reference_tag, rospy.Time(0))
    # # print "trans2",trans2
    # rot_mat2 =listener.fromTranslationRotation(trans2, rot2)
    # rot_mat2 = rot_mat2[:3,:3]
    # # print "rot2",rot_mat2
    # trans,rot = transCentertoWorld(trans2,rot_mat2,trans1,rot_mat1)
    # print "trans,rot",trans,rot
    rospy.sleep(2)
    return trans,rot


def start_robot():
    # init()
    #### verified step:0
    # test_frame_accuracy('robkong','tag_15')
    # robkong_go_to_home(1)

    # test_frame_accuracy('robhong','tag_15')
    # robhong_go_to_home(1)

    #######parameters
    transLocal2Tag,rotLocal2Tag=get_tag_info(referenced_tag="tag_17")
    crease_axis,crease_perp_l,method,angle,crease_length,startP2refP=pg.get_parameters(transLocal2Tag,
                                                                                       rotLocal2Tag,
                                                                                       "step0")
    print "crease axis",crease_axis
    print "crease_perp_l",crease_perp_l
    print "grasp method",method
    print "angle",angle
    print "crease_length",crease_length
    print "startP2refP",startP2refP
    #### verified step: diagonal flexflip
    # crease_axis= [-0.7071, -0.7071, 0]
    # crease_perp_l=0.19
    # crease_length=0.27
    # startP2refP=[0.095,0.03,0] # in world frame

    # trans_target2ref=[0.10,-0.15,0]  # in world frame
    # trans_fix2ref=[0.065,0.135,0]    # in world frame

    # listener.waitForTransform("world", "tag_22", rospy.Time(), rospy.Duration(4.0))
    # (trans_ref,rot_) = listener.lookupTransform("world", 'tag_22', rospy.Time(0))

    # flexflip('tag_22',trans_target2ref, -45.0 , trans_fix2ref, -120.0,crease_axis, crease_perp_l,margin=[0.007,0.007,-0.002])

    # crease(trans_ref,-45.0,crease_axis,crease_length,startP2refP,z_axis=[0,0,1],margin_z=0.005,margin_offset=0.01)

    #### END robotic origmai

    # robhong_go_to_home(1)
    # robkong_go_to_home(1)
    # arduino_pub = rospy.Publisher('/hybrid', UInt16, queue_size=1)
    # rospy.sleep(3)
    # arduino_pub.publish(1)
    # exit()

if __name__=='__main__':
    start_robot()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down")
moveit_commander.os._exit(0)

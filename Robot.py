import datetime
import sys
import threading
import time
import serial
from UtilitiesMacroAndConstant import *
from PVector import PVector
from helper import *
from Vehicle import Vehicle
import numpy as np


class Robot:
    def __init__(self, port, baud_rate, node_log=None):

        self.root_node = node_log
        self.vehicle = Vehicle(CENTER_X, CENTER_Y, MR_WIDTH / 2)

        try:
            if ROS_MODE:
                log(self.root_node, "Opening serial port: %s..." % port + ".")
            else:
                print("Opening serial port: %s..." % port + ".")
            self.robot_serial = serial.Serial(port, baud_rate, timeout=None)
            time.sleep(1)
            self.robot_serial.reset_input_buffer()
            threading.Thread(target=self.flush_data_serial).start()
        except serial.serialutil.SerialException as exp:
            print("Serial not found at port " + port + ".")
            sys.exit(str(exp))

        # Node logging for debuging on ROS
        if ROS_MODE:
            log(self.root_node, "The robot is connected to ", port)
        #  ===============================================

    def flush_data_serial(self):
        self.robot_serial.read(self.robot_serial.in_waiting)
        time.sleep(0.3)

    def write_command(self, cmd):
        cmd = str(cmd)
        self.robot_serial.write(bytes(cmd, 'utf-8'))
        if ROS_MODE:
            log(self.root_node, "\t" + str(datetime.datetime.now().time()) + " --- " + "[[  ", cmd, "  ]]")
        else:
            print("\t" + str(datetime.datetime.now().time()) + " --- " + "[[  ", cmd, "  ]]")

    def read_command(self):
        self.write_command("5,;")
        bytesRead = self.robot_serial.inWaiting()
        return self.robot_serial.read(bytesRead)

    # def receive_data(self):

    def convert_string_to_int32(self, strData):
        return (np.int32(strData[0]) << 24) + (np.int32(strData[1]) << 16) + (np.int32(strData[2]) << 8) + (
            np.int32(strData[3]))

    def nav_mode_control(self, modulus, angle):
        '''
        Receive modulus and angle from navigation mode
        :param modulus:
        :param angle:
        :return:
        '''
        if ROS_MODE:
            log(self.root_node, "\t" + str(datetime.datetime.now().time()) + " --- NAV MODE ---" + "[[  ",
                str(modulus) + "--" + str(angle), "  ]]")
        else:
            print("\t" + str(datetime.datetime.now().time()) + " --- NAV MODE --- " + "[[  ",
                  str(modulus) + "--" + str(angle), "  ]]")

        target_point = PVector
        pass

    def linetrace_mode_control(self, modulus, angle):
        '''
        Receive constant modulus and angle of velocity vector from linetrace algorithm
        :param modulus:
        :param angle:
        :return:
        '''
        if ROS_MODE:
            log(self.root_node, "\t" + str(datetime.datetime.now().time()) + " --- LINETRACE MODE --- " + "[[  ",
                str(modulus) + "--" + str(angle), "  ]]")
        else:
            print("\t" + str(datetime.datetime.now().time()) + " --- LINETRACE MODE --- " + "[[  ",
                  str(modulus) + "--" + str(angle), "  ]]")

    def convert_to_target_point(self):
        pass

    def get_distance_data(self):
        '''
        Get dislocation of 4 wheel apparently
        :return:
        '''
        raw_data = str(self.read_command(), 'utf-8').split()

        # Check length of receive buffer with start and end frame
        if (len(raw_data) == LENGTH_OF_DATA_RECEIVE and raw_data[0] == START_FRAME and raw_data[-1] == END_FRAME):
            receive_data = raw_data[1:-1]
        else:
            return None

        print(receive_data)
        print(receive_data[1:5])
        print(receive_data[6:10])
        print(receive_data[11:15])
        print(receive_data[16:])

        distance_front_left = self.convert_string_to_int32(receive_data[1:5])
        distance_front_right = self.convert_string_to_int32(receive_data[6:10])
        distance_rear_left = self.convert_string_to_int32(receive_data[11:15])
        distance_rear_right = self.convert_string_to_int32(receive_data[16:])

        return distance_front_left, distance_front_right, distance_rear_left, distance_rear_right

    def set_control(self, point):
        self.vehicle.follow(point[0], point[1])

        front_left_angle = (self.vehicle.vel_front_left.heading() - self.vehicle.temporary_left_frame.heading()) * 180 / math.pi
        front_right_angle = (self.vehicle.vel_front_right.heading() - self.vehicle.temporary_right_frame.heading()) * 180 / math.pi
        rear_left_angle = (self.vehicle.vel_rear_left.heading() - self.vehicle.temporary_left_frame.heading()) * 180 / math.pi
        rear_right_angle = (self.vehicle.vel_rear_right.heading() - self.vehicle.temporary_right_frame.heading()) * 180 / math.pi

        front_left_speed = self.vehicle.vel_front_left.mag() / VEL_SCALE
        front_right_speed = self.vehicle.vel_front_right.mag() / VEL_SCALE
        rear_left_speed = self.vehicle.vel_rear_left.mag() / VEL_SCALE
        rear_right_speed = self.vehicle.vel_rear_right.mag() / VEL_SCALE

        # Cover exception returned by atan2 function
        if (front_left_angle < -270):
            front_left_angle += 360
        if (front_right_angle < -270):
            front_right_angle += 360
        if (rear_left_angle < -270):
            rear_left_angle += 360
        if (rear_right_angle < -270):
            rear_right_angle += 360

        if (front_left_angle > 270):
            front_left_angle -= 360
        if (front_right_angle > 270):
            front_right_angle -= 360
        if (rear_left_angle > 270):
            rear_left_angle -= 360
        if (rear_right_angle > 270):
            rear_right_angle -= 360
        # =======================================================

        self.set_speed(front_left_speed, front_right_speed, rear_left_speed, rear_right_speed)
        self.set_steering(front_left_angle, front_right_angle, rear_left_angle, rear_right_angle)

    def set_speed(self, front_left_speed, front_right_speed, rear_left_speed, rear_right_speed):
        self.write_command(
            SPEED_COMMAND + DELIMITER + str(front_left_speed) + DELIMITER + str(front_right_speed) + DELIMITER + str(
                rear_left_speed) + DELIMITER + str(rear_right_speed) + EOF)

    def set_steering(self, front_left_angle, front_right_angle, rear_left_angle, rear_right_angle):
        self.write_command(
            ANGLE_COMMAND + DELIMITER + str(front_left_angle) + DELIMITER + str(front_right_angle) + DELIMITER + str(
                rear_left_angle) + DELIMITER + str(rear_right_angle) + EOF)

    def set_spin(self, angle):
        self.write_command(SPIN_COMMAND + DELIMITER + str(angle) + EOF)
        time.sleep(0.2)

    def get_dislocation(self):
        distance_front_left, distance_front_right, distance_rear_left, distance_rear_right = self.get_distance_data()


if __name__ == "__main__":
    robot = Robot("COM1", 115200)
    front_left_angle = 0
    front_right_angle = 0
    rear_left_angle = 0
    rear_right_angle = 0

    front_left_speed = 0
    front_right_speed = 0
    rear_left_speed = 0
    rear_right_speed = 0

    robot.write_command(
        ANGLE_COMMAND + DELIMITER + str(front_left_angle) + DELIMITER + str(front_right_angle) + DELIMITER + str(
            rear_left_angle) + DELIMITER + str(rear_right_angle) + EOF)
    robot.write_command(
        SPEED_COMMAND + DELIMITER + str(front_left_speed) + DELIMITER + str(front_right_speed) + DELIMITER + str(
            rear_left_speed) + DELIMITER + str(rear_right_speed) + EOF)

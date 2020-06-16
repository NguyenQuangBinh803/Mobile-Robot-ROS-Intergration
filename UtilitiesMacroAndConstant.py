import math

ROS_MODE = False

# Vehicle sufficient macros
VEL_SCALE = 5
MR_HEIGHT = 30
MR_WIDTH = 48
MR_ANGLE = math.atan(MR_HEIGHT / MR_WIDTH)
MR_DISTANCE_FROM_CENTER = math.sqrt((MR_HEIGHT / 2) * (MR_HEIGHT / 2) + (MR_WIDTH / 2) * (MR_WIDTH / 2))
SCALE = 10
MR_SCALE = 5
CENTER_X = 400
CENTER_Y = 400
DISTANCE_BETWWEN_LED = 16
MR_DISTANCE_FROM_CENTER_TO_SENSOR = 100

# Initailize speed and angle value
front_left_angle = 0
front_right_angle = 0
rear_left_angle = 0
rear_right_angle = 0

front_left_speed = 0
front_right_speed = 0
rear_left_speed = 0
rear_right_speed = 0

# Serial parameters
BAUDRATE = 115200
PORT = "COM6"
START_FRAME = "A5"
END_FRAME = "E5"
LENGTH_OF_DATA_RECEIVE = 22


# Serial command format
DELIMITER = ','
ANGLE_COMMAND = 'q'
SPEED_COMMAND = 'n'
DISTANCE_COMMAND = '5'
SPIN_COMMAND = '3'
EOF = ';'



# DELIMITER = ','
# ANGLE_COMMAND = 'q'
# SPEED_COMMAND = 'n'
# EOF = ';'
from math import pi
import common_params as common

def rad2deg(rad):
    return rad * (180 / pi)

# for input string ( "a,b" ) to be array ([a, b])
def convert_str_data(str_data):
    return str(str_data).split(',')

def log(node, *arg, type="info"):
    msg = ""
    for x in arg:
        msg += str(x)
    if type is "warning":
        node.get_logger().warning(msg)
    elif type is "error":
        node.get_logger().error(msg)
    elif type is "fatal":
        node.get_logger().fatal(msg)
    else:
        node.get_logger().info(msg)

# Convert old command from rimocon to mr001 robot
def convert_command(command):
    action = {
        common.UPPER_LEFT: "-45,1000,",
        common.FORWARD: "0,1000,",
        common.UPPER_RIGHT: "45,1000,",
        common.LEFT: "-90,1000,",
        common.RIGHT: "90,1000,",
        common.LOWER_LEFT: "45,-1000,",
        common.BACK: "0,-1000,",
        common.LOWER_RIGHT: "-45,-1000,",
        common.ROTATE_LEFT: "rotate1000,,",
        common.ROTATE_RIGHT: "rotate-1000,,",
        common.STOP: "stop",
        common.RED_STOP: "stop",
        common.SPEED_LEVEL_SLOW: ",," + str(common.SPEED_MIN),
        common.SPEED_LEVEL_MEDIUM: ",," + str(common.SPEED_MEDIUM),
        common.SPEED_LEVEL_FAST: ",," + str(common.SPEED_MAX),
        "off": "off",
        "on": "on"
    }
    try:
        return str(action[command]).split(",")
    except KeyError:
        return [command]

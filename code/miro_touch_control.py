#!/usr/bin/env python

################################################################

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image,CompressedImage
from geometry_msgs.msg import Twist

import miro_msgs
from miro_msgs.msg import platform_config,platform_sensors,platform_state,platform_mics,platform_control,core_state,core_control,core_config,bridge_config,bridge_stream

import math
import numpy
import time
import sys
from miro_constants import miro

from datetime import datetime

################################################################

## IDEA
## Subscribe to the topic /miro/rob01/platform_sensors
## read from that topic the values on the head
## Publish to the topic /miro/rob01/platform_control
## write on linear.x and angular.z 

## NOTE
## 'Main modified stuff' is the place where we modified code, in comparison to orignal demo file.
## 'Deleated stuff' is the place where we deleated code from, in comparison to orignal demo file.

################################################################
def fmt(x, f): #function used for conversion from byteArray to String (The values that we get for the head touch sensors are byteArrays)
    s = ""
    x = bytearray(x)
    for i in range(0, len(x)):
        if not i == 0:
            s = s + ", "
        s = s + f.format(x[i])
    return s

class miro_touch_control_ros_client:

	def callback_platform_sensors(self, subscriber_msg):
		# ignore until active
		if not self.active:
			return

		######## The main modified stuff: read the head touch data from the topic
		
		print "## HEAD DATA ##"
		#print(fmt(subscriber_msg.touch_head, '{0:.0f}')) #Uncomment and see what happens in output, It converts from byteArray to str

		A = int(fmt(subscriber_msg.touch_head, '{0:.0f}')[0]) # Sensor at 16'oclock on head
		B = int(fmt(subscriber_msg.touch_head, '{0:.0f}')[3]) # Sensor at 14'oclock on head
		C = int(fmt(subscriber_msg.touch_head, '{0:.0f}')[6]) # Sensor at 10'oclock on head
		D = int(fmt(subscriber_msg.touch_head, '{0:.0f}')[9]) # Sensor at 20'oclock on head
		
		cliff=map(int, fmt(subscriber_msg.cliff, '{0:.0f}').split(", "))

		E = int(fmt(subscriber_msg.touch_body, '{0:.0f}')[0]) # Sensor at 16'oclock on head
		F = int(fmt(subscriber_msg.touch_body, '{0:.0f}')[3]) # Sensor at 14'oclock on head
		G = int(fmt(subscriber_msg.touch_body, '{0:.0f}')[6]) # Sensor at 10'oclock on head
		H = int(fmt(subscriber_msg.touch_body, '{0:.0f}')[9]) # Sensor at 20'oclock on head
		
		#print(type(subscriber_msg.cliff))
		######## The main modified stuff: print the head touch data from the topic

		print "## A ==>", A
		print "## B ==>", B
		print "## C ==>", C
		print "## D ==>", D
		print "==="
		print "## E ==>", E
		print "## F ==>", F
		print "## G ==>", G
		print "## H ==>", H

		####### The main modified stuff: drive MiRo using touch data

		q = platform_control()
		self.body_vel = Twist()
		if cliff[0] and cliff[1] > 5:
			if A == 1 and D == 0:
				print "turn right"
				self.body_vel.angular.z = -1.5708
			if D == 1 and A == 0:
				print "turn left"
				self.body_vel.angular.z = +1.5708
			if B == 1 and C == 1:
				print "go backward"
				self.body_vel.linear.x = -250
			if A == 1 and D == 1:
				print "go forward"
				self.body_vel.linear.x = +250
			if E == 1 or F == 1 or G == 1 or H == 1:
				print "go forward"
				self.body_vel.linear.x = +250
		else:
			self.body_vel.linear.x = 0
			self.body_vel.angular.z = 0

		# publish
		q.body_vel = self.body_vel
		self.pub_platform_control.publish(q)

####### Deleated some functions from here (compared to the orignal file)

	def loop(self):
		while True:
			print "in the loop function"
			if rospy.core.is_shutdown():
				break
			time.sleep(1)
			print "tick"
			if rospy.core.is_shutdown():
				break
			time.sleep(1)
			print "tock"

	def __init__(self):

		# report
		print("initialising...")
		print(sys.version)
		print(datetime.time(datetime.now()))

		# default data
		self.platform_sensors = None

		# no arguments gives usage
		if len(sys.argv) == 1:
			usage()

		# options
		self.robot_name = ""
		self.drive_pattern = ""

		# handle args
		for arg in sys.argv[1:]:
			f = arg.find('=')
			if f == -1:
				key = arg
				val = ""
			else:
				key = arg[:f]
				val = arg[f+1:]
			if key == "robot":
				self.robot_name = val
			elif key == "drive":
				self.drive_pattern = val
			else:
				error("argument not recognised \"" + arg + "\"")

		# check we got at least one
		if len(self.robot_name) == 0:
			error("argument \"robot\" must be specified")

		# set inactive
		self.active = False

		# topic root
		topic_root = "/miro/" + self.robot_name
		print "topic_root", topic_root

		# publish
		self.pub_platform_control = rospy.Publisher(topic_root + "/platform/control", platform_control, queue_size=0)
		####### Deleated some functions from here (compared to the orignal file)

		# subscribe
		self.sub_sensors = rospy.Subscriber(topic_root + "/platform/sensors", platform_sensors, self.callback_platform_sensors)
		####### Deleated some functions from here (compared to the orignal file)

		# set active
		self.active = True

if __name__ == "__main__":
	rospy.init_node("miro_touch_control_ros_client_py", anonymous=True)
	main = miro_touch_control_ros_client()
	main.loop()

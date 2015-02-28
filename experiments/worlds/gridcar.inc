# gridcar.inc
# Emulates the robot from GridWorld
# Author: James Marshall
# Date: Feb 21 2013

define gridcar_sensor sensor
(
	size [0.01 0.1 0.2]
	range [0 30.0]
	fov 5
	samples 1
)

define gridcar_sonars ranger
(
	# Units are in meters from the origin, angles in degrees
	# 16 sensors all at the same point (I don't think it matters)
	# counter-clockwise from front (right) facing
	gridcar_sensor( pose [ 0 0 -0.1 0 ] )
	gridcar_sensor( pose [ 0 0 -0.1 22.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 45 ] )
	gridcar_sensor( pose [ 0 0 -0.1 67.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 90 ] )
	gridcar_sensor( pose [ 0 0 -0.1 112.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 135] )
	gridcar_sensor( pose [ 0 0 -0.1 157.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 180] )
	gridcar_sensor( pose [ 0 0 -0.1 202.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 225] )
	gridcar_sensor( pose [ 0 0 -0.1 247.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 270] )
	gridcar_sensor( pose [ 0 0 -0.1 292.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 315] )
	gridcar_sensor( pose [ 0 0 -0.1 337.5 ] )
)

define gridcar_sonars_2 ranger
(
	# Units are in meters from the origin, angles in degrees
	# 16 sensors all at the same point (I don't think it matters)
	# counter-clockwise from front (right) facing
	gridcar_sensor( pose [ 0 0 -0.1 0 ] )
	gridcar_sensor( pose [ 0 0 -0.1 22.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 45 ] )
	gridcar_sensor( pose [ 0 0 -0.1 67.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 90 ] )
	gridcar_sensor( pose [ 0 0 -0.1 112.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 135] )
	gridcar_sensor( pose [ 0 0 -0.1 157.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 180] )
	gridcar_sensor( pose [ 0 0 -0.1 202.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 225] )
	gridcar_sensor( pose [ 0 0 -0.1 247.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 270] )
	gridcar_sensor( pose [ 0 0 -0.1 292.5 ] )
	gridcar_sensor( pose [ 0 0 -0.1 315] )
	gridcar_sensor( pose [ 0 0 -0.1 337.5 ] )
)

define gridcar position
(
	# Scaled to 1 unit = 4 cm
	size [0.24 0.272 0.16]
	# center of rotation offset
	origin [-.04 0 0 0]

	# Main body
	block 
	(
		points 4
		point[0] [0 1.6]
		point[1] [6 1.6]
		point[2] [6 5.2]
		point[3] [0 5.2]
		z [0 4]
	)
	
	# Left Wheel
	block
	(
		points 4
		point[0] [2 5.2]
		point[1] [6 5.2]
		point[2] [6 6.8]
		point[3] [2 6.8]
		z [0 4]
	)

	# Right Wheel
	block
	(
		points 4
		point[0] [2 0]
		point[1] [6 0]
		point[2] [6 1.6]
		point[3] [2 1.6]
		z [0 4]
	)

	drive "diff"

	localization "gps"	

	gridcar_sonars()
	gridcar_sonars_2()

	obstacle_return 1	# can hit things
#	laser_return 1		# seen by lasers
	ranger_return 1		# seen by sonar
	blob_return 1 		# seen by blobfinders	
	
)
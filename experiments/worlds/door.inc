# door.inc
# It's a wall, that will move. Hopefully splitting a convoy.
#
# Author: James Marshall
# Date: July 26 2013

define door_sensor sensor
(
	size [0.01 0.1 0.2]
	range [0 30.0]
	fov 5
	samples 1
)

define door_sonars ranger
(
	# Units are in meters from the origin, angles in degrees
	door_sensor( pose [ 0 0 -0.1 0 ] )
)


define door position
(
	# Scaled to 1 unit = 4 cm
	size [2.0 0.24 0.16]
	# center of rotation offset
	origin [0 0 0 0]

	# Main body
	block 
	(
		points 4
		point[0] [0 0]
		point[1] [50 0]
		point[2] [50 6]
		point[3] [0 6]
		z [0 4]
	)
	
	drive "omni"

	door_sonars()

	obstacle_return 1	# can hit things
	laser_return 1		# seen by lasers
	ranger_return 1		# seen by sonar
	blob_return 1 		# seen by blobfinders	
)
#!/usr/bin/env python3	

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32, Float32MultiArray
import matplotlib.pyplot as plt
from matplotlib import animation
import threading
import numpy as np
import math

# Variables globales
global posBall, rho, alpha, beta

# Constantes del controlador de velocidad
kp = 0.3
kalpha = 0.8
kbeta = 0.1

# Posicion del robot para la grafica
posSIMx = []
posSIMy = []

# Posicion de la pelota
posBall = [ 0, 0 ]

# Coordenadas para la transformacion
rho = 0
alpha = 0
beta = 0

def callbackPos (msg):
	global posBall, rho, alpha, beta

	posSIMx.append(msg.linear.x)
	posSIMy.append(msg.linear.y)

	# Diferencial de la posicion
	dX = posBall[0] - msg.linear.x
	dY = posBall[1] - msg.linear.y

	# Transformacion de coordenadas
	rho = np.sqrt( dX**2 + dY**2 )
	alpha = -msg.angular.z + math.atan2( dY, dX )
	beta = -msg.angular.z - alpha


def callbackBallPos (msg):
	global posBall

	posBall = msg.data


def graficar(a):
	plt.cla()	# Se borra informacion anterior al ploteo actual
	plt.plot( posSIMx, posSIMy )	# Plotea las variables
	plt.axis([ -6.6, 6.6, -5, 5 ])	#Define limites en X y Y (limites de la cancha)


def grafica():
	objeto = animation.FuncAnimation(plt.figure(1), graficar, 10000)
	plt.show()


def soccer_player():
	global rho, alpha,beta

	# Inicializa el nodo.
	rospy.init_node('soccer_futbol_player', anonymous=True)

	#Inicializa los Subscribers
	rospy.Subscriber('robot_Position', Twist, callbackPos)
	rospy.Subscriber('ball_Position', Float32MultiArray, callbackBallPos)

	# Inicializa los Publishers
	pubKick = rospy.Publisher('kick_power', Float32, queue_size=10)
	pubVel = rospy.Publisher('robot_move_vel', Twist, queue_size=10)

	# Crea el thread para la grafica en tiempo real
	graph = threading.Thread(target=grafica)
	graph.start()

	rate = rospy.Rate(10)	#10Hz

	#Inicializa los mensajes
	msgVel = Twist()
	msgKick = Float32()

	while not rospy.is_shutdown():

		# Actualiza los datos dependiendo del valor de alpha
		v = kp*rho
		w = kalpha*alpha + kbeta*beta

		if alpha >= -np.pi/2 and alpha <= np.pi/2:
			
			nrho = -np.cos(alpha)*v
			nalpha = np.sin(alpha)/rho*v - w
			nbeta = -np.sin(alpha)/rho*v
		else:
			
			nrho = -np.cos(alpha)*v
			nalpha = -np.sin(alpha)/rho*v + w
			nbeta = np.sin(alpha)/rho*v

		# Actualiza los valores
		rho += nrho
		alpha += nalpha
		nbeta += beta

		# Define las velocidades lineal y angular
		v = kp*rho
		w = kalpha*alpha + kbeta*beta
		
		# Asigna datos a los mensajes
		msgVel.linear.x =	v	# TODO: Asignar valores
		msgVel.linear.y = 0	# TODO: Asignar valores
		msgVel.angular.z = w	# TODO: Asignar valores

		msgKick.data = 0	# TODO: Asignar valores

		# Publica los mensajes en el topic respectivo.
		pubVel.publish(msgVel)
		pubKick.publish(msgKick)

		rate.sleep()


if __name__ == '__main__':
	try:
		soccer_player()
	except rospy.ROSInterruptException:
		pass
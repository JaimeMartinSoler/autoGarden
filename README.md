About RPi-Arduino connections:
	- When comunicating over GPIO, connect RPi_GND to Arduino_GND with a shortcut or RPi will read nothing but noise
	- Run the program first in the device that outputs (Arduino in this case) to stabilize the signal and then run the program in the device that inputs (RPi in this case) so that the input signal was already stable
	

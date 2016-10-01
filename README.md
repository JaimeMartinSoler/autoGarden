# AUTOMATIC GARDEN

[Automatic Garden] developed with **Arduino** and **Raspberry Pi**, that irrigates itself and tweets about temperature, humidity, etc. Check a real time example in [circuits.io].

 

--------------------------------------------------------------------------------
## SETUP: SOFWARE
Depending on the communication interface we are using (GPIO wires, NRF24L wireless) and the sensor (analog LM35, digital DHT22), there are different library setups to make:

 

### GPIO wired communication
Take into account the following points:
- Connect any RPi_GND to any Arduino_GND with a shortcut. Otherwise the RPi will read nothing but noise.
- Before running the RPi programm, run the Arduino programm and make the conections. Otherwise the RPi will start with a few random reads.

 

### NRF24L wireless 2.4GHz transciever: Arduino
Download the following library:
[https://github.com/tmrh20/RF24]

 

### NRF24L wireless 2.4GHz transciever: Raspberry Pi
This setup is based in the instructions you can find in [akirasan.net] and [raspberrypi.org/spi].

**1. Install python, RPi.GPIO, smbus, i2c-tools:**
```sh
sudo apt-get update
sudo apt-get install python-dev
sudo apt-get install python3-dev
sudo apt-get install python-rpi.gpio
sudo apt-get install python-smbus
sudo apt-get install i2c-tools
```

**2. Edit file `/etc/modules`:** 
```sh
sudo nano /etc/modules
```
adding the following lines on the bottom: 
```sh
i2c-bcm2708
i2c-dev
```

**3. Edit file `/etc/modprobe.d/raspi-blacklist.conf`:** 
```sh
sudo nano /etc/modprobe.d/raspi-blacklist.conf
```
commenting out the following lines (adding `'#'` as first character): 
```sh
#blacklist spi-bmc2708
#blacklist i2c-bmc2708
```

**4. Install library nrf24.py:** 
```sh
cd autoGarden/src/RPi
wget https://raw.githubusercontent.com/jpbarraca/pynrf24/master/nrf24.py
```

**5. Install library python-spi:** 
```sh
cd /lib
sudo mkdir py-spidev
cd py-spidev
sudo wget https://raw.github.com/doceme/py-spidev/master/setup.py 
sudo wget https://raw.github.com/doceme/py-spidev/master/spidev_module.c
sudo touch README.md
sudo touch CHANGELOG.md
sudo python ./setup.py install
```

**6. Enable SPI master driver and I2C**:  
There are two ways to do this:  
  - **6.a. Enable SPI and I2C graphically from `raspi-config`**:
```sh
sudo raspi-config
```
and choose 'Advanced Options', 'SPI', 'Yes', and also 'Advanced Options', 'I2C', 'Yes'. Then, reboot the Raspberry Pi.
```sh
sudo reboot
```
  - **6.b. Enable SPI and I2C manually from `/boot/config.txt`**:
```sh
sudo nano /boot/config.txt
```
add the following lines:
```sh
dtparam=spi=on
dtparam=i2c_arm=on
```
save the changes and reboot the Raspberry Pi:
```sh
sudo reboot
```

  - **Check that `/dev/spidev0.0` and `/dev/spidev0.0` files exist**:  
By doing this (any of the ways to enable SPI and I2C), the following 2 files should have been created, check that both exist:
```sh
/dev/spidev0.0
/dev/spidev0.1
```
#### Other notes:
- **If you are getting errors with python-spi, install it this way:** 
```sh
cd /lib
sudo mkdir python-spi 
cd python-spi 
sudo wget https://github.com/doceme/py-spidev/archive/master.zip
sudo unzip master.zip
cd py-spidev-master
sudo python ./setup.py install
```

 

 

--------------------------------------------------------------------------------
## LICENSE
Under development.




[Automatic Garden]:  <https://github.com/JaimeMartinSoler/autoGarden>
[circuits.io]: <https://circuits.io/circuits/2723637-autogardenr>
[akirasan.net]: <http://www.akirasan.net/raspbpi-arduino-com-bidireccional-nrf24l01/>
[raspberrypi.org/spi]: <https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md>
[https://github.com/tmrh20/RF24]: <https://github.com/tmrh20/RF24>




[//]: # (.md editor: <http://dillinger.io/>)
[//]: # (.md cheatsheet: <https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet>)
[//]: # (Invisible character for extra line breaking " ": <http://stackoverflow.com/questions/17978720/invisible-characters-ascii>)

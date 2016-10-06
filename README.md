# AUTOMATIC GARDEN

[Automatic Garden] developed with **Arduino** and **Raspberry Pi**, that irrigates itself and tweets about temperature, humidity, etc. Check a real time example in [circuits.io].

 

--------------------------------------------------------------------------------
## SETUP: SOFWARE
Depending on the communication interface we are using (GPIO wires, NRF24L wireless) and the sensor (analog LM35, digital DHT22), there are different library setups to make:

 

### GPIO wired communication
Take into account the following points:
- [Arduino GPIO reference], and more.
- [Raspberry Pi GPIO python reference].
- Install the GPIO python library in the Raspberry Pi:  
  ```sh
  sudo apt-get install python-rpi.gpio
  ```
- Connect any RPi_GND to any Arduino_GND with a shortcut. Otherwise the RPi will read nothing but noise.
- Before running the RPi programm, run the Arduino programm and make the conections. Otherwise the RPi will start with a few random reads.

 

### NRF24L wireless 2.4GHz transciever: Arduino
- **Install the [TMRh20/RF24] library:**  
Arduino IDE menu bar > Sketch > Include Library > Manage Libraries... > Type "RF24" in the search field > Install the "RF24 by TMRh20" library.  
(The library can be downloaded from the repository [https://github.com/tmrh20/RF24], but the cleanest way to do it is from the Arduino IDE)

 

### NRF24L wireless 2.4GHz transciever: Raspberry Pi
This setup is based in the instructions you can find in [invent.module143].

**1. Enable SPI master driver and I2C**:  
There are two ways to do this:  
  - **1.a. Enable SPI and I2C graphically from `raspi-config`**:  
    ```
    sudo raspi-config
    ```  
    and choose 'Advanced Options', 'SPI', 'Yes', and also 'Advanced Options', 'I2C', 'Yes'. Then, reboot the Raspberry Pi.  
    ```
    sudo reboot
    ```  
  - **1.b. Enable SPI and I2C manually from `/boot/config.txt`**:  
    `sudo nano /boot/config.txt`  
    add the following lines:  
    `dtparam=spi=on`  
    `dtparam=i2c_arm=on`  
    save the changes and reboot the Raspberry Pi:  
    `sudo reboot`  
Finnaly, check that `/dev/spidev0.0` and `/dev/spidev0.1` files exist.  


**2. Install python, RPi.GPIO, smbus, i2c-tools:**
```sh
sudo apt-get update
sudo apt-get install python-dev
sudo apt-get install python3-dev
sudo apt-get install python-rpi.gpio
sudo apt-get install python-smbus
sudo apt-get install i2c-tools
```

**(3. Mybe not-necessary: Edit file `/etc/modules`):** 
```sh
sudo nano /etc/modules
```
adding the following lines on the bottom: 
```sh
i2c-bcm2708
i2c-dev
```

**(4. Mybe not-necessary: Edit file `/etc/modprobe.d/raspi-blacklist.conf`):** 
```sh
sudo nano /etc/modprobe.d/raspi-blacklist.conf
```
commenting out the following lines (adding `'#'` as first character): 
```sh
#blacklist spi-bmc2708
#blacklist i2c-bmc2708
```

**5. Install library [py-spidev]:** 
```sh
cd /lib
sudo mkdir py-spidev
cd py-spidev
sudo wget https://github.com/Gadgetoid/py-spidev/archive/master.zip
sudo unzip master.zip
cd py-spidev-master
sudo python3 setup.py install
```

**6. Install library [lib_nrf24.py]:** 
```sh
cd autoGarden/src/RPi
wget https://github.com/BLavery/lib_nrf24/blob/master/lib_nrf24.py
```

 

 

--------------------------------------------------------------------------------
## LICENSE
Under development.




[Automatic Garden]:  <https://github.com/JaimeMartinSoler/autoGarden>
[circuits.io]: <https://circuits.io/circuits/2723637-autogardenr>
[Arduino GPIO reference]: <https://www.arduino.cc/en/Reference/HomePage>
[Raspberry Pi GPIO python reference]: <https://sourceforge.net/p/raspberry-gpio-python/wiki/Examples/>
[TMRh20/RF24]: <http://tmrh20.github.io/RF24/>
[https://github.com/tmrh20/RF24]: <https://github.com/tmrh20/RF24>
[invent.module143]: <http://invent.module143.com/daskal_tutorial/rpi-3-tutorial-14-wireless-pi-to-arduino-communication-with-nrf24l01/>
[py-spidev]: <https://github.com/Gadgetoid/py-spidev>
[lib_nrf24.py]: <https://github.com/BLavery/lib_nrf24>




[//]: # (.md editor: <http://dillinger.io/>)
[//]: # (.md cheatsheet: <https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet>)
[//]: # (Invisible character for extra line breaking " ": <http://stackoverflow.com/questions/17978720/invisible-characters-ascii>)
[//]: # (other [unsuccessful] NRF24 tutorial: <http://www.akirasan.net/raspbpi-arduino-com-bidireccional-nrf24l01/>)

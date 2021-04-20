# rpiGreenhouse
Automate greenhouse using Raspberry Pi

1. Update

sudo apt-get update --yes && sudo apt-get upgrade --yes
sudo apt-get install build-essential python-dev python-pip python-smbus python-openssl git --yes

2.1 Intall pigpio

wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install
cd ..

If the Python part of the install fails it may be because you need the setup tools.

sudo apt install python-setuptools python3-setuptools

2.2 Start daemon on boot

sudo systemctl enable pigpiod

3. Copy code

mkdir greenhouse
scp ~/[source dir]/*.py pi@[your rpi IP]]:/home/pi/greenhouse/

4. RTC

wget https://raw.githubusercontent.com/tutRPi/Raspberry-Pi-Greenhouse/master/SDL_DS1307.py

5. MCP3008

wget https://raw.githubusercontent.com/tutRPi/Raspberry-Pi-Greenhouse/master/MCP3008.py

6. Log rotate

mkdir log
sudo vi /etc/logrotate.conf

/home/pi/log/greenhouse.log {
    daily
    missingok
    rotate 10
    compress
    delaycompress
    notifempty
    copytruncate
}

7. Run code
`
crontab -e

@reboot       sudo python /home/pi/greenhouse/button.py >> /home/pi/log/greenhouse.log 2>&1
45 07 * * *   sudo python /home/pi/greenhouse/waterPlants.py >> /home/pi/log/greenhouse.log 2>&1
10 *  * * *   sudo python /home/pi/greenhouse/readTemperature.py >> /home/pi/log/greenhouse.log 2>&1
15 *  * * *   sudo python /home/pi/greenhouse/measureMoisture.py >> /home/pi/log/greenhouse.log 2>&1
`

8. Config

sudo raspi-config

Select “Interfacing Options” and activate:
* SSH
* SPI
* I2C

...save

sudo reboot

9. Install SPI

git clone https://github.com/doceme/py-spidev
cd py-spidev
sudo python setup.py install
cd ..

10. Check logs

cat log/greenhouse.log

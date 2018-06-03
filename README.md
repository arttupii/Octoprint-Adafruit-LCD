# Adafruit 16x2 LCD 

Displays printer progress while printing on a [Adafruit 16x2 LCD](https://www.adafruit.com/product/1115) attached 
to a [Rasperry Pi](http://www.raspberrypi.org). This makes it easy to see print progress without the need to look 
at [OctoPrint](http://www.octoprint.org).

![progress image](https://raw.githubusercontent.com/ttocsneb/Octoprint-Adafruit-LCD/master/readme_resources/print_progress.jpg)

<details><summary><b>more images</b></summary>
<p>

![print started](https://raw.githubusercontent.com/ttocsneb/Octoprint-Adafruit-LCD/master/readme_resources/print_start.jpg)
    
![print started](https://raw.githubusercontent.com/ttocsneb/Octoprint-Adafruit-LCD/master/readme_resources/print_done.jpg)
</p>
</details>

## Setup

### Attaching the LCD

You can use either the [adafruit pi 16x2 hat](https://www.adafruit.com/product/1115), or the [adafruit Arduino 16x2 shield](https://www.adafruit.com/product/772).  They are the same, except one fits the Raspberry Pi while the other fits the Arduino Uno--I'm use the Uno version from an old project.

If you are connecting the the lcd remotely (not directly ontop of the pi), you will only need to connect 4 wires: 5V(4), GND(6), SDA(3), SCL(5).

<details><summary><b>Pinout Examples</b> (click me!)</summary>
<p>

#### Pinout on Raspberry Pi

[![pinout.xyz](https://raw.githubusercontent.com/ttocsneb/Octoprint-Adafruit-LCD/master/readme_resources/raspi_pinout.png)](https://pinout.xyz/pinout/)

#### Pinout on Pi Hat LCD

![16x2 hat](https://raw.githubusercontent.com/ttocsneb/Octoprint-Adafruit-LCD/master/readme_resources/pi_pinout.png)

#### Pinout on Uno Shield LCD

![16x2 shield](https://raw.githubusercontent.com/ttocsneb/Octoprint-Adafruit-LCD/master/readme_resources/uno_pinout.png)

</p>
</details>

### Requirements before install

Both the smbus and i2c-tools packages should be installed, before installing the plugin.

    sudo apt-get install python-smbus i2c-tools

### Install instructions
Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager) using this URL:

    https://github.com/ttocsneb/Octoprint-Adafruit-LCD/archive/master.zip

### Troubleshooting

If you are getting errors about missing libraries, try manually installing the adafruit library

    source ~/oprint/bin/activate # ignore this if you are not using a virtual environment
    #replace 'oprint' with your virtual environment if you are not running Octopi
    git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git ~/devel/Adafruit_Python_CharLCD
    cd ~/devel/Adafruit_Python_CharLCD
    sudo python setup.py install

 If you are still getting errors, try following the [adafruit setup guide](https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi/usage). 

## Configuration

*Configuration to be added in future versions*

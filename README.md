# OctoPrint-Piprint

Displays printer progress while printing on a [Adafruit 16x2 LCD](http://www.adafruit.com/search?q=16x2+pi&b=1) attached 
to a [Rasperry Pi](http://www.raspberrypi.org). This makes it easy to see print progress without the need to look 
at [OctoPrint](http://www.octoprint.org).

![Piprint example](http://i.imgur.com/hzxQAVA.jpg "Piprint Example")

## Setup
You must perform a bit of setup and configuration before using this plugin.

### Requirements before setup

Both the smbus and i2c-tools packages should be installed, before installing the plugin.

    sudo apt-get install python-smbus i2c-tools

### Setup instructions
Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager) using this URL:

    https://github.com/evilsoapbox/OctoPrint-Piprint/archive/master.zip

### Troubleshooting

If you are getting errors when installing with the bundled Plugin Manager, try manually installing the dependents with the folowing commands.

    source ~/oprint/bin/activate # ignore this if you are not using a virtual environment
    #replace 'oprint' with your virtual environment if you are not running Octopi
    sudo apt-get update
    sudo apt-get install build-essential python-smbus i2c-tools
    sudo pip install RPi.GPIO

If you are still getting errors, try manually installing the adafruit library

    source ~/oprint/bin/activate # again, ignore this if you don't use a virtual environment
    #don't forget to change 'oprint' if you are not using Octopi
    git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git ~/devel/Adafruit_Python_CharLCD
    cd ~/devel/Adafruit_Python_CharLCD
    sudo python setup.py install

 The instructions came from the [adafruit setup guide](https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi/usage). 

## Configuration

*Configuration to be added in future versions*

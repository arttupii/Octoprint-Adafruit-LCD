# coding=utf-8
from __future__ import absolute_import
import Adafruit_CharLCD as LCD
import octoprint.plugin
import math
import re

from . import lcdutil
from . import lcddata

class Adafruit_16x2_LCD(octoprint.plugin.StartupPlugin,
                    octoprint.plugin.ProgressPlugin,
                    octoprint.plugin.ShutdownPlugin,
                    octoprint.plugin.EventHandlerPlugin):
    
    def __init__(self):
        # constants

        self.__lcd = LCD.Adafruit_CharLCDPlate()

        
        self.__data = lcddata.LCDData()
        self.__lcdutil = lcdutil.LCDUtil(self.__lcd, self.__data)

        self.__filename = ""

        

    def on_after_startup(self):
        """
        Runs when plugin is started. Turn on and clear the LCD.
        """

        self.__lcdutil.init(self._logger)

        self._logger.debug("Starting Verbose Debugger")
        self._logger.info("Adafruit 16x2 LCD starting")

        self.__lcdutil.clear()
        self.__lcdutil.write_to_lcd("Hello! What will", 0, False)
        self.__lcdutil.write_to_lcd("we print today?", 1, False)
        
        

    def on_event(self, event, payload):
        # type (str, dict)
        """
        Called when an event occurs. Displays print updates; turns off LCD when print stops for any reason.
        :param event: Event which just happened.
        :param payload: Dictionary of data passed with the event
        """

        # Only let useful events continue
        # 'onnect' encapsulates any Connection event
        useful_events = ['Print', 'onnect', 'Error', 'Slicing', 'MetadataAnalysisFinished', 'Shutdown']
        black_list = ['ConnectivityChanged', 'PrinterStateChanged']
        if any(e in event for e in useful_events) and not any(e in event for e in black_list):
            self._logger.info("Event: {}".format(event))
        else:
            return
        
        # Make sure the lcd is enabled for the event
        self.__lcdutil.light(True, True)

        # clear the screen before printing anything for any event that should be cleared beforehand
        clear_screen_events = ['onnect', 'Slicing', 'Error', 'MetadataAnalysisFinished', 'PrintDone', 'PrintStarted']
        if any(e in event for e in clear_screen_events):
            self.__lcdutil.clear()

        # simple events that should only need the event printed
        simple_events = ['onnect', 'Print', 'Error', 'Slicing']
        if any(e in event for e in simple_events):
            self.__lcdutil.write_to_lcd(event, 0)

        # special implementation for events

        # turn on the lcd if any event has been triggered other than Disconnected
        if event == 'Disconnected' or event == 'Shutdown':
            self.__lcdutil.clear()
            self.__lcdutil.enable_lcd(False, True)
            self.__lcdutil.light(False, True)
        else:
            self.__lcdutil.enable_lcd(True)
        
        if event == 'Error':
            self.__lcdutil.write_to_lcd(payload["error"], 1, False)
        
        elif event == 'PrintDone':
            seconds = payload["time"]
            hours = int(math.floor(seconds / 3600))
            minutes = int(math.floor(seconds / 60) % 60)
            self.__lcdutil.write_to_lcd("Time: {} h,{} m".format(hours, minutes), 1, False)
        
        elif event == 'PrintStarted':
            name = payload["name"]
            # Clean up the file name to better fit the screen
            name = self.__data.clean_file_name(name)
            self.__lcdutil.write_to_lcd(name, 1, False)
            self.__filename = name
            # Create custom progress bar every time a print starts
            self._create_custom_progress_bar()

        elif event == 'MetadataAnalysisFinished':
            self.__lcdutil.write_to_lcd("Analysis Finish", 0, False)
            self.__lcdutil.write_to_lcd(self.__data.clean_file_name(payload["name"]), 1, False)
        
        elif "Slicing" in event and "Profile" not in event:
            self.__lcdutil.write_to_lcd(self.__data.clean_file_name(payload["stl"]), 1, False)
            if event == 'SlicingDone':
                min = int(math.floor(payload["time"] / 60))
                sec = int(math.floor(payload["time"]) % 60)
                text = "SlicingDone {}:{}".format(min, sec)
                if len(text) > 16:
                    text = text.replace(" ", "")
                self.__lcdutil.write_to_lcd(text, 0, False)
        

    def on_print_progress(self, storage, path, progress):
        # type (str, str, int)
        """
        Called on 1% print progress updates. Displays the new progress on the LCD.
        :param storage: File being printed
        :param path: Path of file being printed
        :param progress: Progress of print
        """
        if not self._printer.is_printing() or progress == 0:
            return
        
        self.__lcdutil.write_to_lcd(self.__filename, 0)
        self.__lcdutil.write_to_lcd(self._format_progress_bar(progress), 1)

    def on_shutdown(self):
        """
        Called on shutdown of OctoPrint. Turn off the LCD.
        """
        self._logger.info("Turning off LCD")
        self.__lcdutil.light(False, True)

    # Class methods (assisting functions)
    def _create_custom_progress_bar(self):
        """
        Load the custom progress bar into the lcd screen
        """
        self.__lcd.create_char(ord(self.__data.perc2), [0, 0, 0b10000, 0, 0b10000, 0, 0, 0])
        self.__lcd.create_char(ord(self.__data.perc4), [0, 0, 0b11000, 0, 0b11000, 0, 0, 0])
        self.__lcd.create_char(ord(self.__data.perc6), [0, 0, 0b11100, 0, 0b11100, 0, 0, 0])
        self.__lcd.create_char(ord(self.__data.perc8), [0, 0, 0b11110, 0, 0b11110, 0, 0, 0])

    

    def _format_progress_bar(self, progress):
        # type (int) -> None
        """
        Create a formatted string 'progress bar' based on the given value
        :param progress: Progress (0-100) of the print
        :return: Formatted string representing a progress bar
        """

        switcher = {
            0: ' ',
            1: self.__data.perc2,
            2: self.__data.perc4,
            3: self.__data.perc6,
            4: self.__data.perc8,
            5: self.__data.perc10
        }

        bar = self.__data.perc10 * int(round(progress / 10))
        bar += switcher[(progress % 10) / 2]
        bar += ' ' * (10 - len(bar))
        
        return "[{}] {}%".format(bar, str(progress))

    
    
    

__plugin_name__ = "Adafruit 16x2 LCD"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Adafruit_16x2_LCD()
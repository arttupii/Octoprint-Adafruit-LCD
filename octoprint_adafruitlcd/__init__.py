# coding=utf-8
from __future__ import absolute_import
import Adafruit_CharLCD as LCD
import octoprint.plugin
import math

class Adafruit_16x2_LCD(octoprint.plugin.StartupPlugin,
                    octoprint.plugin.ProgressPlugin,
                    octoprint.plugin.ShutdownPlugin,
                    octoprint.plugin.EventHandlerPlugin):
    
    def __init__(self):
        # constants

        self.__lcd_width = 16

        self.__2perc = unichr(1)
        self.__4perc = unichr(2)
        self.__6perc = unichr(3)
        self.__8perc = unichr(4)
        self.__10perc = '='

        self.__lcd_state = False
        self.__current_lcd_text = [" " * self.__lcd_width, " " * self.__lcd_width]


        self.__lcd = LCD.Adafruit_CharLCDPlate()

        self.__filename = ""

        self.__lcd.clear()
        self.__lcd.home()
        self.__lcd.message("I'm waking up\njust wait a sec")

    def on_after_startup(self):
        """
        Runs when plugin is started. Turn on and clear the LCD.
        """

        self._logger.debug("Starting Verbose Debugger")
        self._logger.info("Adafruit 16x2 LCD starting")

        self._clear()
        self._write_to_lcd("Hello! What will", 0, False)
        self._write_to_lcd("we print today?", 1, False)
        
        

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

        # clear the screen before printing anything for any event that should be cleared beforehand
        clear_screen_events = ['onnect', 'Slicing', 'Error', 'MetadataAnalysisFinished', 'PrintDone', 'PrintStarted']
        if any(e in event for e in clear_screen_events):
            self._clear()

        # simple events that should only need the event printed
        simple_events = ['onnect', 'Print', 'Error', 'Slicing']
        if any(e in event for e in simple_events):
            self._write_to_lcd(event, 0)

        # special implementation for events

        # turn on the lcd if any event has been triggered other than Disconnected
        if event == 'Disconnected' or event == 'Shutdown':
            self._clear()
            self._turn_lcd_off(True)
        else:
            self._turn_lcd_on(True)
        
        if event == 'Error':
            self._write_to_lcd(payload["error"], 1, False)
        
        elif event == 'PrintDone':
            seconds = payload["time"]
            hours = int(math.floor(seconds / 3600))
            minutes = int(math.floor(seconds / 60) % 60)
            self._write_to_lcd("Time: {} h,{} m".format(hours, minutes), 1, False)
        
        elif event == 'PrintStarted':
            name = payload["name"]
            self._write_to_lcd(payload["name"], 1, False)
            self.__filename = payload["name"]
            # Create custom progress bar every time a print starts
            self._create_custom_progress_bar()

        elif event == 'MetadataAnalysisFinished':
            self._write_to_lcd("Analysis Finish", 0, False)
            self._write_to_lcd(payload["name"], 1, False)
        
        elif "Slicing" in event and "Profile" not in event:
            self._write_to_lcd(payload["stl"], 1, False)
            if event == 'SlicingDone':
                min = int(math.floor(payload["time"] / 60))
                sec = int(math.floor(payload["time"]) % 60)
                text = "SlicingDone {}:{}".format(min, sec)
                if len(text) > 16:
                    text = text.replace(" ", "")
                self._write_to_lcd(text, 0, False)
        

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
        
        self._write_to_lcd(self.__filename, 0)
        self._write_to_lcd(self._format_progress_bar(progress), 1)

    def on_shutdown(self):
        """
        Called on shutdown of OctoPrint. Turn off the LCD.
        """
        self._logger.info("Turning off LCD")
        self._turn_lcd_off(True)

    # Class methods (assisting functions)
    def _create_custom_progress_bar(self):
        self.__lcd.create_char(ord(self.__2perc), [0, 0, 0b10000, 0, 0b10000, 0, 0, 0])
        self.__lcd.create_char(ord(self.__4perc), [0, 0, 0b11000, 0, 0b11000, 0, 0, 0])
        self.__lcd.create_char(ord(self.__6perc), [0, 0, 0b11100, 0, 0b11100, 0, 0, 0])
        self.__lcd.create_char(ord(self.__8perc), [0, 0, 0b11110, 0, 0b11110, 0, 0, 0])

    def _clear(self):
        """
        Clear both the lcd and the internal buffer.
        
        Prefer this method to clearing the lcd directly.
        """

        self.__lcd.clear()
        self.__current_lcd_text = [" " * self.__lcd_width, " " * self.__lcd_width]

    def _format_progress_bar(self, progress):
        # type (int)
        """
        Create a formatted string 'progress bar' based on the given value
        :param progress: Progress (0-100) of the print
        :return: Formatted string representing a progress bar
        """

        switcher = {
            0: ' ',
            1: self.__2perc,
            2: self.__4perc,
            3: self.__6perc,
            4: self.__8perc,
            5: self.__10perc
        }

        bar = self.__10perc * int(round(progress / 10))
        bar += switcher[(progress % 10) / 2]
        bar += ' ' * (10 - len(bar))
        
        return "[{}] {}%".format(bar, str(progress))

    def _turn_lcd_off(self, force=False):
        # type (bool)
        """
        Turn the LCD off by setting the backlight to zero.
        :param force: ignore the __lcd_state value
        """

        self._logger.debug("turning lcd on; forced: {}".format(force))

        if self.__lcd_state or force:
            self.__lcd.set_backlight(0)
            self.__lcd_state = False

    def _turn_lcd_on(self, force=False):
        # type (bool)
        """
        Turn the LCD on by setting the backlight to one.
        :param force: ignore the __lcd_state value
        """

        self._logger.debug("turning lcd off; forced: {}".format(force))

        if not self.__lcd_state or force:
            self.__lcd.set_backlight(1.0)
            self.__lcd_state = True

    def _write_to_lcd(self, message, row, clear=True, column=0):
        # type (str, int, bool, int)
        """
        Write a string message to the LCD. Displays the text on the LCD display.
        :param message: Message to display on the LCD
        :param row: Line number to display the text
        :param clear: clear the line
        :param column: position to start writing
        """
        self._logger.info("Writing to LCD: {}".format(self._special_chars_to_num(message)))

        self._turn_lcd_on()

        # make sure the message fits in the display
        message = message[:self.__lcd_width - column]
        # if the message should clear the line, fill the rest of the line with spaces
        if clear:
            temp = " " * self.__lcd_width
            # insert the message into a lcd_width blank string
            message = temp[:column] + message + temp[column + len(message):]
            # clear the column number since we will now write to the entire line
            column = 0


        # find the positions of the characters that are different
        diff = self._get_diff(self.__current_lcd_text[row][column:], message)

        # save the message to an array so that we can store what's actually being written
        m = list(self.__current_lcd_text[row])

        self._logger.debug("Writing characters:")

        # write each different character
        last = -1
        for i in diff:
            # If the next character to write is not next to the last written 
            # character, go to the new location
            if last != i:
                self.__lcd.set_cursor(column + i, row)
            # Write the next character
            self.__lcd.write8(ord(message[i]), True)
            m[column + i] = message[i]
            self._logger.debug("  {}".format(self._special_chars_to_num(str(message[i]))))

            # set last to the selected index
            last = i + 1

        # update the lcd buffer with the newly written text
        self.__current_lcd_text[row] = "".join(m)


        self._logger.debug("LCD now displays: ")
        self._logger.debug("  '{}'".format(self._special_chars_to_num(self.__current_lcd_text[0])))
        self._logger.debug("  '{}'".format(self._special_chars_to_num(self.__current_lcd_text[1])))

    def _special_chars_to_num(self, string):
        #type (str) -> str
        """
        Convert special characters that the LCD uses to numbers in the format '#0' or '#5'

        The range is 0 to 7 since the LCD can only store 8 special characters
        """
        for ch in range(0, 8):
            if unichr(ch) in string:
                string = string.replace(unichr(ch), "#{}".format(ch))
        return string
    
    def _get_diff(self, str1, str2):
        #type (str, str) -> list
        """
        Get the indexes for each difference in the two strings.  The two strings 
        don't have to be the same size
        :param str1: string 1
        :param str2: string 2
        """
        return [i for i in xrange(min(len(str1), len(str2))) if str1[i] != str2[i]]
    

__plugin_name__ = "Adafruit 16x2 LCD"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Adafruit_16x2_LCD()
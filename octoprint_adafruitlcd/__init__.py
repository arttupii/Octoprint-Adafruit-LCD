# coding=utf-8
from __future__ import absolute_import
import Adafruit_CharLCD as LCD
import octoprint.plugin
import math

class Adafruit_16x2_LCD(octoprint.plugin.StartupPlugin,
                    octoprint.plugin.ProgressPlugin,
                    octoprint.plugin.ShutdownPlugin,
                    octoprint.plugin.EventHandlerPlugin):

    __lcd_width = 16

    __2perc = 1
    __4perc = 2
    __6perc = 3
    __8perc = 4
    __10perc = 5

    __2percstr = '\x01'
    __4percstr = '\x02'
    __6percstr = '\x03'
    __8percstr = '\x04'
    __10percstr = '\x05'

    __lcd_state = False

    __current_lcd_text = None

    __lcd = None

    __filename = ""

    def on_after_startup(self):
        """
        Runs when plugin is started. Turn on and clear the LCD.
        """
        self._logger.info("PiPrint starting")
        lcd = self._get_lcd()

        # create the loading characters
        lcd.create_char(self.__2perc, [16, 16, 16, 16, 16, 16, 16, 0])
        lcd.create_char(self.__4perc, [24, 24, 24, 24, 24, 24, 24, 0])
        lcd.create_char(self.__6perc, [28, 28, 28, 28, 28, 28, 28, 0])
        lcd.create_char(self.__8perc, [30, 30, 30, 30, 30, 30, 30, 0])
        lcd.create_char(self.__10perc,[31, 31, 31, 31, 31, 31, 31, 0])

        self._clear()

        self._turn_lcd_off(True)
        

    def on_event(self, event, payload):
        """
        Called when an event occurs. Displays print updates; turns off LCD when print stops for any reason.
        :param event: Event which just happened.
        :param payload: Dictionary of data passed with the event
        """

        lcd = self._get_lcd()

        clear_screen_events = ['Connected', 'Disconnected']
        if any(e in event for e in clear_screen_events):
            self._clear()

        # events to print the name of
        useful_events = ['Connected', 'PrintPaused', 'PrintResumed', 'PrintStarted']
        if any(e in event for e in useful_events):
            self._write_to_lcd(event, 0)


        #custom implementation for events

        if 'Disconnected' not in event:
            self._turn_lcd_on()

        if 'Disconnected' in event:
            self._turn_lcd_off(True)
        
        if 'Error' in event:
            self._write_to_lcd(event, 0)
            self._write_to_lcd(payload["error"], 1)
        
        if 'PrintDone' in event:
            self._write_to_lcd("Print Done", 0)
            seconds = payload["time"]
            hours = math.floor(seconds / 3600)
            minutes = math.floor(seconds / 60) % 60
            self._write_to_lcd("Time: %d h,%d m" % (hours, minutes), 1)
        
        if 'PrintStarted' in event:
            name = payload["name"]
            self._write_to_lcd(payload["name"], 1)
            self.__filename = payload["name"]

        

    def on_print_progress(self, storage, path, progress):
        """
        Called on 1% print progress updates. Displays the new progress on the LCD.
        :param storage: File being printed
        :param path: Path of file being printed
        :param progress: Progress of print
        """
        if not self._printer.is_printing():
            return
        
        if progress == 0:
            return

        self._write_to_lcd(self.__filename, 0)
        self._write_to_lcd(self._format_progress_bar(progress), 1)

    def on_shutdown(self):
        """
        Called on shutdown of OctoPrint. Turn off the LCD.
        """
        self._logger.info("PiPrint turning off LCD")
        self._turn_lcd_off()

    # Class methods (assisting functions)
    def _clear(self):
        """
        Clear both the lcd and the internal buffer.
        
        Prefer this method to clearing the lcd directly.
        """
        lcd = self._get_lcd()
        lcd.clear()
        self.__current_lcd_text = [" " * self.__lcd_width, " " * self.__lcd_width]

    def _format_progress_bar(self, progress):
        """
        Create a formatted string 'progress bar' based on the given value
        :param progress: Progress (0-100) of the print
        :return: Formatted string representing a progress bar
        """

        switcher = {
            1: self.__2percstr,
            2: self.__4percstr,
            3: self.__6percstr,
            4: self.__8percstr,
            5: self.__10percstr
        }

        filler = self.__10percstr * int(round(progress / 10)) + switcher.get((progress % 10) / 2, " ")
        spaces = " " * (10 - len(filler))
        return "[{}{}] {}%".format(filler, spaces, str(progress))

    def _turn_lcd_off(self, force=False):
        """
        Turn the LCD off by setting the backlight to zero.
        :param force: ignore the __lcd_state value
        """
        lcd = self._get_lcd()

        if self.__lcd_state or force:
            lcd.set_backlight(0)
            self.__lcd_state = False

    def _turn_lcd_on(self, force=False):
        """
        Turn the LCD on by setting the backlight to one.
        :param force: ignore the __lcd_state value
        """
        lcd = self._get_lcd()

        if not self.__lcd_state or force:
            lcd.set_backlight(1.0)
            self.__lcd_state = True

    def _write_to_lcd(self, message, row, clear=True, column=0):
        """
        Write a string message to the LCD. Displays the text on the LCD display.
        :param message: Message to display on the LCD
        :param row: Line number to display the text
        :param clear: clear the line
        :param column: position to start writing
        """
        self._logger.info("Writing to LCD: " + message)

        lcd = self._get_lcd()
        self._turn_lcd_on()

        if self.__current_lcd_text == None:
            self.__current_lcd_text = [" " * self.__lcd_width, " " * self.__lcd_width]

        # make sure the message fits in the display
        message = message[:self.__lcd_width - column]
        # if the message should clear the line, fill the rest of the line with spaces
        if clear:
            message = (" " * column) + message + (" " * (self.__lcd_width - len(message) - column))


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
                lcd.set_cursor(column + i, row)
            # Write the next character
            lcd.write8(ord(message[i]), True)
            m[column + i] = message[i]
            self._logger.debug("  " + message[i])

            # set last to the selected index
            last = i + 1

        # update the lcd buffer with the newly written text
        self.__current_lcd_text[row] = "".join(m)

        self._logger.debug("LCD now displays: ")
        self._logger.debug("  '{}'".format(self.__current_lcd_text[0]))
        self._logger.debug("  '{}'".format(self.__current_lcd_text[1]))

    
    def _get_diff(self, str1, str2):
        """
        Get the indexes for each difference in the two strings.  The two strings 
        don't have to be the same size
        :param str1: string 1
        :param str2: string 2
        """
        return [i for i in xrange(min(len(str1), len(str2))) if str1[i] != str2[i]]
    
    def _get_lcd(self):
        # type: () -> LCD
        """
        Get the LCD instance

        For use with the Unit Tester

        """
        if self.__lcd == None:
            self.__lcd = LCD.Adafruit_CharLCDPlate()
        return self.__lcd
    
    def _get_lcd_text(self, row):
        return self.__current_lcd_text[row]

__plugin_name__ = "Adafruit 16x2 LCD"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Adafruit_16x2_LCD()
# coding=utf-8
from __future__ import absolute_import
import Adafruit_CharLCD as LCD
import octoprint.plugin
import math

class PiprintPlugin(octoprint.plugin.StartupPlugin,
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

    __current_lcd_text = [" " * __lcd_width, " " * __lcd_width]

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

        lcd.clear()

        self._turn_lcd_off(True)
        

    def on_event(self, event, payload):
        """
        Called when an event occurs. Displays print updates; turns off LCD when print stops for any reason.
        :param event: Event which just happened.
        :param payload: Dictionary of data passed with the event
        """
        # events to print the name of
        useful_events = ['Connected', 'PrintPaused', 'PrintResumed', 'PrintStarted']
        if any(e in event for e in useful_events):
            self.__class__._write_to_lcd(event, 0)

        lcd = self.__class__._get_lcd()

        #custom implementation for events

        if 'Disconnected' in event:
            lcd.clear()
            self.__class__._turn_lcd_off()
        
        if 'Connected' in event:
            self.__class__._turn_lcd_on()
        
        if 'Error' in event:
            self.__class__._write_to_lcd("%s:%s" % (event, payload["error"]), 0)
        
        if 'PrintDone' in event:
            self.__class__._write_to_lcd("Print Done", 0)
            seconds = payload["time"]
            hours = math.floor(seconds / 3600)
            minutes = math.floor(seconds / 60) % 60
            self.__class__._write_to_lcd("Time: %d h,%d m" % (hours, minutes), 1)
        
        if 'PrintStarted' in event:
            name = payload["name"]
            self.__class__._write_to_lcd(payload["name"], 1)
            self.__class__.__filename = payload["name"]

        

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

        self.__class__._write_to_lcd(self.__class__.__filename, 0)
        self.__class__._write_to_lcd(self.__class__._format_progress_bar(progress), 1)

    def on_shutdown(self):
        """
        Called on shutdown of OctoPrint. Turn off the LCD.
        """
        self._logger.info("PiPrint turning off LCD")
        self.__class__._turn_lcd_off()

    # Class methods (assisting functions)
    @classmethod
    def _format_progress_bar(cls, progress):
        """
        Create a formatted string 'progress bar' based on the given value
        :param progress: Progress (0-100) of the print
        :return: Formatted string representing a progress bar
        """

        switcher = {
            1: cls.__2percstr,
            2: cls.__4percstr,
            3: cls.__6percstr,
            4: cls.__8percstr,
            5: cls.__10percstr
        }

        filler = cls.__10percstr * int(round(progress / 10)) + switcher.get((progress % 10) / 2, " ")
        spaces = " " * (10 - len(filler))
        return "[{}{}] {}%".format(filler, spaces, str(progress))

    @classmethod
    def _turn_lcd_off(cls, force=False):
        """
        Turn the LCD off by setting the backlight to zero.
        :param force: ignore the __lcd_state value
        """
        lcd = cls._get_lcd()

        if cls.__lcd_state or force:
            lcd.set_backlight(0)
            cls.__lcd_state = False

    @classmethod
    def _turn_lcd_on(cls, force=False):
        """
        Turn the LCD on by setting the backlight to one.
        :param force: ignore the __lcd_state value
        """
        lcd = cls._get_lcd()

        if not cls.__lcd_state or force:
            lcd.set_backlight(1.0)
            cls.__lcd_state = True

    @classmethod
    def _write_to_lcd(cls, message, row, clear=True, column=0):
        """
        Write a string message to the LCD. Displays the text on the LCD display.
        :param message: Message to display on the LCD
        :param row: Line number to display the text
        :param clear: clear the line
        :param column: position to start writing
        """
        lcd = cls._get_lcd()

        # make sure the message fits in the display
        message = message[:cls.__lcd_width - column]
        if clear:
            message = message + (" " * (cls.__lcd_width - len(message)))

        cls._turn_lcd_on()

        # find the positions of the characters that are different
        diff = cls._get_diff(cls.__current_lcd_text[row][column:], message)

        #print the whole string if it has changed too much
        if len(diff) > 4:
            lcd.set_cursor(column, row)
            for char in message:
                lcd.write8(ord(char), True)
            cls.__current_lcd_text[row] = cls.__current_lcd_text[row][column:] + message
            return
        
        m = list(cls.__current_lcd_text[row])

        #write only the different characters
        for i in diff:
            lcd.set_cursor(column + i, row)
            lcd.write8(ord(message[i]), True)
            m[column + i] = message[i]
        
        cls.__current_lcd_text[row] = "".join(m)
    
    @classmethod
    def _get_diff(cls, str1, str2):
        """
        Get the indexes for each difference in the two strings.  The two strings 
        don't have to be the same size
        :param str1: string 1
        :param str2: string 2
        """
        return [i for i in xrange(min(len(str1), len(str2))) if str1[i] != str2[i]]
    
    @classmethod
    def _get_lcd(cls):
        if cls.__lcd == None:
            cls.__lcd = LCD.Adafruit_CharLCDPlate()
        return cls.__lcd

__plugin_name__ = "Adafruit 16x2 LCD"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PiprintPlugin()
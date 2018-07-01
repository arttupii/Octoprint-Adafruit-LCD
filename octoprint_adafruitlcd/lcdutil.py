
import math
import re
import Adafruit_CharLCD as LCD

from . import lcddata

class LCDUtil:

    def __init__(self, lcd, data):
        # type (Adafruit_CharLCDPlate, LCDData) -> None
        """
        Create a new LCDUtil object.  It holds basic utility commands for the LCD
        :lcd: lcd to use
        """

        self.__data = data

        self.__lcd_enabled = True
        self.__lcd_light = False
        self.__current_lcd_text = [" " * self.__data.lcd_width, " " * self.__data.lcd_width]

        self.__lcd = lcd

        self.__lcd.enable_display(True)
        self.__lcd.clear()
        self.__lcd.home()
        self.__lcd.message("Hold on, I'm\nstill waking up")

    def init(self, logger):
        # type (Logger)
        self._logger = logger

    def enable_lcd(self, enable, force=False):
        # type (bool, bool) -> None
        """
        Enable or disable the display
        :enable: True to enable
        :force: Force the display to enable/disable
        """

        if force:
            self._logger.info("{}abling lcd; forced: yes".format('En' if enable else 'Dis'))
            self.__lcd.enable_display(enable)
            self.__lcd_enabled = enable
        else:
            if self.__lcd_enabled != enable:
                self._logger.info("{}abling lcd; forced: no".format('En' if enable else 'Dis'))
                self.__lcd.enable_display(enable)
                self.__lcd_enabled = enable

    def light(self, on, force=False):
        # type (bool, bool) -> None
        """
        Turn on or off the LCD backlight
        :param on: True to turn on the light
        :param force: Force the light on or off
        """

        if force:
            self._logger.debug("turning {} lcd light; forced: Yes".format('on' if on else 'off'))
            self.__lcd.set_backlight(1.0 if on else 0)
            self.__lcd_light = on
        else:
            if self.__lcd_light != on:
                self._logger.debug("turning {} lcd light; forced: No".format('on' if on else 'off'))
                self.__lcd.set_backlight(1.0 if on else 0)
                self.__lcd_light = on

    def write_to_lcd(self, message, row, clear=True, column=0):
        # type (str, int, bool, int)
        """
        Write a string message to the LCD. Displays the text on the LCD display.
        :param message: Message to display on the LCD
        :param row: Line number to display the text
        :param clear: clear the line
        :param column: position to start writing
        """
        self._logger.info("Writing to LCD: {}".format(self.__data.special_chars_to_num(message)))

        self.enable_lcd(True)
        self.light(True)

        # make sure the message fits in the display
        message = message[:self.__data.lcd_width - column]
        # if the message should clear the line, fill the rest of the line with spaces
        if clear:
            temp = " " * self.__data.lcd_width
            # insert the message into a lcd_width blank string
            message = temp[:column] + message + temp[column + len(message):]
            # clear the column number since we will now write to the entire line
            column = 0


        # find the positions of the characters that are different
        diff = self.__data.get_diff(self.__current_lcd_text[row][column:], message)

        # save the message to an array so that we can store what's actually being written
        m = list(self.__current_lcd_text[row])

        self._logger.debug("Writing characters:")

        # write each different character
        if len(diff) > 0:
            last = diff[0]
            self.__lcd.set_cursor(column + diff[0], row)
        for i in diff:
            # If the next character to write is not next to the last written 
            # character, go to the new location
            if last != i:
                self.__lcd.set_cursor(column + i, row)
            # Write the next character
            self.__lcd.write8(ord(message[i]), True)
            m[column + i] = message[i]
            self._logger.debug("  {}".format(self.__data.special_chars_to_num(str(message[i]))))

            # set last to the selected index
            last = i + 1

        # update the lcd buffer with the newly written text
        self.__current_lcd_text[row] = "".join(m)


        self._logger.debug("LCD now displays: ")
        self._logger.debug("  '{}'".format(self.__data.special_chars_to_num(self.__current_lcd_text[0])))
        self._logger.debug("  '{}'".format(self.__data.special_chars_to_num(self.__current_lcd_text[1])))

    def clear(self):
        """
        Clear both the lcd and the internal buffer.
        
        Prefer this method to clearing the lcd directly.
        """

        self.__lcd.clear()
        self.__current_lcd_text = [" " * self.__data.lcd_width, " " * self.__data.lcd_width]
    
    

    


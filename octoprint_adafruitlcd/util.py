
import math
import re
import Adafruit_CharLCD as LCD

from octoprint_adafruitlcd.data import getLogger
from octoprint_adafruitlcd import data

_lcd_enabled = True
_lcd_light = False
_current_lcd_text = [" " * data.lcd_width, " " * data.lcd_width]


def init():
    """
    Setup the LCD screen.
    """

    # Write starting message to lcd
    data.lcd.enable_display(True)
    data.lcd.clear()
    data.lcd.home()
    data.lcd.message("Hold on, I'm\nstill waking up")


def enable_lcd(enable, force=False):
    # type (bool, bool) -> None
    """
    Enable or disable the display
    :enable: True to enable
    :force: Force the display to enable/disable
    """

    global _lcd_enabled

    if force:
        getLogger().info("{}abling lcd; forced: yes".format(
                         'En' if enable else 'Dis'))
        data.lcd.enable_display(enable)
        _lcd_enabled = enable
    else:
        if _lcd_enabled is not enable:
            getLogger().info("{}abling lcd; forced: no".format(
                             'En' if enable else 'Dis'))
            data.lcd.enable_display(enable)
            _lcd_enabled = enable


def light(on, force=False):
    # type (bool, bool) -> None
    """
    Turn on or off the LCD backlight
    :param on: True to turn on the light
    :param force: Force the light on or off
    """

    global _lcd_light

    if force:
        getLogger().debug("turning {} lcd light; forced: Yes".format(
                          'on' if on else 'off'))
        data.lcd.set_backlight(1.0 if on else 0)
        _lcd_light = on
    else:
        if _lcd_light is not on:
            getLogger().debug("turning {} lcd light; forced: No".format(
                              'on' if on else 'off'))
            data.lcd.set_backlight(1.0 if on else 0)
            _lcd_light = on


def write_to_lcd(message, row, clear=True, column=0):
    # type (str, int, bool, int)
    """
    Write a string message to the LCD. Displays the text on the LCD
    display.

    :param message: Message to display on the LCD
    :param row: Line number to display the text
    :param clear: clear the line
    :param column: position to start writing
    """
    getLogger().info("Writing to LCD: {}".format(
                     data.special_chars_to_num(message)))

    # make sure the message fits in the display
    message = message[:data.lcd_width - column]
    # if the message should clear the line, fill the rest of the line with
    # spaces
    if clear:
        temp = " " * data.lcd_width
        # insert the message into a lcd_width blank string
        message = temp[:column] + message + temp[column + len(message):]
        # clear the column number since we will now write to the entire
        # line
        column = 0

    # find the positions of the characters that are different
    diff = data.get_diff(_current_lcd_text[row][column:],
                         message)

    # save the message to an array so that we can store what's actually
    # being written
    m = list(_current_lcd_text[row])

    # getLogger().debug("Writing characters:")

    # write each different character
    if len(diff) > 0:
        last = diff[0]
        data.lcd.set_cursor(column + diff[0], row)
    for i in diff:
        # If the next character to write is not next to the last written
        # character, go to the new location
        if last is not i:
            data.lcd.set_cursor(column + i, row)
        # Write the next character
        data.lcd.write8(ord(message[i]), True)
        m[column + i] = message[i]
        # getLogger().debug("  {}".format(data.special_chars_to_num(
        #              str(message[i]))))

        # set last to the selected index
        last = i + 1

    # update the lcd buffer with the newly written text
    _current_lcd_text[row] = "".join(m)

    getLogger().debug("LCD now displays: ")
    getLogger().debug("  '{}'".format(data.special_chars_to_num(
                      _current_lcd_text[0])))
    getLogger().debug("  '{}'".format(data.special_chars_to_num(
                      _current_lcd_text[1])))


def clear():
    """
    Clear both the lcd and the internal buffer.

    Prefer this method to clearing the lcd directly.
    """

    global _current_lcd_text

    data.lcd.clear()
    _current_lcd_text = [" " * data.lcd_width, " " * data.lcd_width]


def create_custom_progress_bar():
    """
    Load the custom progress bar into the lcd screen
    """
    data.lcd.create_char(ord(data.perc2),
                         [0, 0, 0b10000, 0, 0b10000, 0, 0, 0])
    data.lcd.create_char(ord(data.perc4),
                         [0, 0, 0b11000, 0, 0b11000, 0, 0, 0])
    data.lcd.create_char(ord(data.perc6),
                         [0, 0, 0b11100, 0, 0b11100, 0, 0, 0])
    data.lcd.create_char(ord(data.perc8),
                         [0, 0, 0b11110, 0, 0b11110, 0, 0, 0])

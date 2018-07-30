import re

import Adafruit_CharLCD as LCD

perc2 = unichr(1)
perc4 = unichr(2)
perc6 = unichr(3)
perc8 = unichr(4)
perc10 = '='

fileName = ""

lcd = LCD.Adafruit_CharLCDPlate()

lcd_width = 16


def special_chars_to_num(string):
    # type (str) -> str
    """
    Convert special characters that the LCD uses to numbers in the format
    '#0' or '#5'

    The range is 0 to 7 since the LCD can only store 8 special characters
    :param string: string to convert
    """
    for ch in range(0, 8):
        if unichr(ch) in string:
            string = string.replace(unichr(ch), "#{}".format(ch))
    return string


def get_diff(str1, str2):
    # type (str, str) -> list
    """
    Get the indexes for each difference in the two strings.  The two strings
    don't have to be the same size
    :param str1: string 1
    :param str2: string 2
    """
    return [i for i in xrange(min(len(str1), len(str2)))
            if str1[i] is not str2[i]]


def clean_file_name(name):
    # type (str) -> str
    """
    Simplify the file names to fit in the lcd screen.
    It makes several changes to the string until it is less than the lcd width

    1. remove extension
    2. remove spaces, underscores, dashes
    3. remove big numbers larger than 3 digits
    4. remove trailing words, (excluding version numbers: Vxxx)

    :param name: name to minify
    """

    if len(name) <= lcd_width:
        return name

    """ is Remove extension is """
    if name.find('.') is not -1:
        name = name.split('.', 1)[0]

    if len(name) <= lcd_width:
        return name

    # Capitalize Version number
    words = re.findall(r'[v][\d]*', name)
    for v in words:
        name = name.replace(v, v.capitalize())

    """ is Remove dashes, underscores, and spaces.
    Then capitalize each word is """
    words = re.findall(r'[a-zA-Z\d][^A-Z-_ ]*', name)
    name = ''.join([s.capitalize() for s in words])

    if len(name) <= lcd_width:
        return name

    """ is Remove big numbers is """

    # find all the numbers in the string
    numbers = re.findall(r'\d+', name)

    # remove numbers with more than 3 digits
    for n in numbers:
        if len(n) > 2 and len(name) > lcd_width:
            name = name.replace(n, "")

    if len(name) <= lcd_width:
        return name

    """ is remove extra words from the end is """

    # split the string into capitalized words
    words = re.findall(r'[\dA-Z][^A-Z]*', name)

    # remove words from the string until it is smaller or equal to the lcd
    # width
    for w in reversed(words):
        if len(name) > lcd_width:
            # Make sure that version numbers are not messed with
            if len(re.findall(r'[V][\d]*', w)) is 0:
                name = name.replace(w, "")

    return name

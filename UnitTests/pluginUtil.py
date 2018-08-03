import logging

import octoprint_adafruitlcd as adafruitLCD

from dummyPrinter import DummyPrinter

printer = DummyPrinter()


def getLCDText(text):
    # type: (TestPlugin, str) -> str
    text = text[:16]
    return text + " " * (16 - len(text))


def getPlugin():
    adafruitLCD.__plugin_load__()
    plugin = adafruitLCD.__plugin_implementation__

    # Setup logger
    logging.basicConfig()
    plugin._logger = logging.getLogger("logging")

    plugin._logger.setLevel(40)  # error
    # plugin._logger.setLevel(20)  # info
    # plugin._logger.setLevel(10)  # debug

    # Setup Printer
    plugin._printer = printer

    plugin.on_startup(None, None)
    plugin.on_after_startup()

    return plugin


def getLCD():
    return adafruitLCD.data.lcd


def getLCDBuffer(row):
    return adafruitLCD.util._current_lcd_text[row]

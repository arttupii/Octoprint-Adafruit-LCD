# coding=utf-8
from __future__ import absolute_import
import Adafruit_CharLCD as LCD
import octoprint.plugin
import octoprint.util
import math
import re


from octoprint_adafruitlcd import globalVars
from octoprint_adafruitlcd import data
from octoprint_adafruitlcd import util
from octoprint_adafruitlcd import events
from octoprint_adafruitlcd.printerStats import PrinterStats


class Adafruit_16x2_LCD(octoprint.plugin.StartupPlugin,
                        octoprint.plugin.ProgressPlugin,
                        octoprint.plugin.ShutdownPlugin,
                        octoprint.plugin.EventHandlerPlugin):

    def __init__(self):
        # constants

        util.init()

    def on_after_startup(self):
        """
        Runs when plugin is started. Turn on and clear the LCD.
        """

        events.carousel.init()

        self._logger.debug("Starting Verbose Debugger")
        self._logger.info("Adafruit 16x2 LCD starting")

        self._printer.register_callback(PrinterStats())

        util.clear()
        util.write_to_lcd("Hello! What will", 0, False)
        util.write_to_lcd("we print today?", 1, False)

    def on_event(self, event, payload):
        # type (str, dict)
        """
        Called when an event occurs. Displays print updates, slicing info,
        alalysis times, ect.

        If there are more than one on_event call at a time, then it will

        :param event: Event which just happened.
        :param payload: Dictionary of data passed with the event
        """

        # Only let useful events continue
        # 'onnect' encapsulates any Connection event
        # 'Anal' encapsulates any MetaData Analysing events
        useful_events = ['Print', 'onnect', 'Error', 'Slicing', 'Anal',
                         'Shutdown', 'self_']
        black_list = ['ConnectivityChanged', 'PrinterStateChanged', 'Profile']
        if any(e in event for e in useful_events) and \
           not any(e in event for e in black_list):
            self._logger.info("Event: {}".format(event))
        else:
            return

        events.on_event(event, payload)

    def on_print_progress(self, storage, path, progress):
        # type (str, str, int)
        """
        Called on 1% print progress updates. Displays the new progress on the
        LCD.

        :param storage: File being printed
        :param path: Path of file being printed
        :param progress: Progress of print
        """
        if not self._printer.is_printing() or progress is 0 or progress is 100:
            return

        # send this event to the event manager
        events.on_event("self_progress", {'progress': progress,
                        'name': data.fileName})

    def on_slicing_progress(self, slicer, source_location, source_path,
                            destination_location, destination_path, progress):
        # type (str, str, str, str, str, int) -> None
        """
        Called on 1% slicing progress updates. Displays the new progress on
        the LCD.

        :param storage: File being printed
        :param path: Path of file being printed
        :param progress: Progress of print
        """

        if progress is 0 or progress is 100:
            return

        events.on_event("self_progress", {'progress': progress,
                        'name': data.fileName})

    def on_shutdown(self):
        """
        Called on shutdown of OctoPrint. Turn off the LCD.
        """
        self._logger.info("Turning off LCD")
        util.light(False, True)
        util.enable_lcd(False, True)


__plugin_name__ = "Adafruit 16x2 LCD"


def __plugin_load__():
    global __plugin_implementation__
    globalVars.plugin_instance = Adafruit_16x2_LCD()
    __plugin_implementation__ = globalVars.plugin_instance

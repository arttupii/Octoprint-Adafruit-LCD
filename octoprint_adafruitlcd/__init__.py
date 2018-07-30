# coding=utf-8
from __future__ import absolute_import
import Adafruit_CharLCD as LCD
import octoprint.plugin
import math
import re

import octoprint_adafruitlcd
from . import util
from . import synchronousEvent
from . import events


class Adafruit_16x2_LCD(octoprint.plugin.StartupPlugin,
                        octoprint.plugin.ProgressPlugin,
                        octoprint.plugin.ShutdownPlugin,
                        octoprint.plugin.EventHandlerPlugin):

    def __init__(self):
        # constants

        self.__util = util.LCDUtil()
        self.__events = events.Events(self.__util)

        self.__filename = ""

        self.__synchronous_events = synchronousEvent.SynchronousEventQueue()
        self.__is_LCD_printing = False

    def on_after_startup(self):
        """
        Runs when plugin is started. Turn on and clear the LCD.
        """

        self.__util.init(self._logger)

        self._logger.debug("Starting Verbose Debugger")
        self._logger.info("Adafruit 16x2 LCD starting")

        self.__util.clear()
        self.__util.write_to_lcd("Hello! What will", 0, False)
        self.__util.write_to_lcd("we print today?", 1, False)

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

        # start a synchronous event if there are no events waiting to be
        # executed
        if not self.__is_LCD_printing:
            self.__is_LCD_printing = True
            self.synchronous_event(self.__synchronous_events, event, payload)
            self.__is_LCD_printing = False
        else:
            e = synchronousEvent.SynchronousEvent(event, payload)
            self.__synchronous_events.put(e)

    def synchronous_event(self, eventManager, event, payload):
        # type (SynchronousEventQueue, str, dict) -> None
        """
        Can not be called asynchronously.  To protect from asynchronous
        calls, use the SynchronousEventQueue class
        """
        self._logger.info("Processing Event: {}".format(event))

        # Make sure the lcd is enabled for the event
        self.__util.light(True)

        # Connect events
        if 'onnect' in event:
            self.__events.on_connect_event(event, payload)

        elif event == 'Error':
            self.__events.on_error_event(event, payload)

        elif 'Print' in event:
            self.__events.on_print_event(event, payload)

        elif 'Anal' in event:
            self.__events.on_analysys_event(event, payload)

        elif "Slicing" in event:
            self.__events.on_slicing_event(event, payload)

        elif event == 'self_progress':
            self.__events.on_progress_event(event, payload)

        """ Start the next synchronous event if there are any events waiting
        in the queue """

        if not eventManager.empty():
            e = eventManager.pop()
            self.synchronous_event(eventManager, e.getEvent(), e.getPayload())

    def on_print_progress(self, storage, path, progress):
        # type (str, str, int)
        """
        Called on 1% print progress updates. Displays the new progress on the
        LCD.

        :param storage: File being printed
        :param path: Path of file being printed
        :param progress: Progress of print
        """
        if not self._printer.is_printing() or progress == 0 or progress == 100:
            return

        # pass the progress onto the event manager, so that no to LCD prints
        # will happen at the same time.
        # I know that this is a bit convoluted, but it works for now
        self.on_event("self_progress", {'progress': progress,
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

        if progress == 0 or progress == 100:
            return

        self.on_event("self_progress", {'progress': progress,
                      'name': data.fileName})

    def on_shutdown(self):
        """
        Called on shutdown of OctoPrint. Turn off the LCD.
        """
        self._logger.info("Turning off LCD")
        self.__util.light(False, True)
        self.__util.enable_lcd(False, True)


__plugin_name__ = "Adafruit 16x2 LCD"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Adafruit_16x2_LCD()

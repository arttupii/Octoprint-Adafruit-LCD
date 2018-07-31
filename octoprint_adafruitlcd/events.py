import math

import octoprint.util

from octoprint_adafruitlcd import data
from octoprint_adafruitlcd import util
from octoprint_adafruitlcd.printerStats import PrinterStats


"""
All events from octoprint are implemented here

The main on_event function is still in __init__.py,
but the implementation is located in events.py

Any events called will not check if the event type
is actually correct, the event variable is used for
differentiating between more specific events
"""

_progress = 0
_name = ''


def on_print_event(event, payload):
    # type (str, dict) -> None

    util.write_to_lcd(event, 0)

    if event is 'PrintDone':
        carousel.timer.cancel()
        util.write_to_lcd("Time: " + format_time(payload['time']), 1)
        return

    if event is 'PrintStarted':
        util.create_custom_progress_bar()
        data.fileName = data.clean_file_name(payload['name'])
        util.write_to_lcd(data.fileName, 1)
        carousel.timer.start()


def on_connect_event(event, payload):
    # type (str, dict) -> None

    util.clear()

    # turn off the lcd
    if event is 'Disconnected':
        util.light(False, True)
        util.enable_lcd(False, True)
        return

    # write the event to the screen
    util.write_to_lcd(event, 0, False)


def on_error_event(event, payload):
    # type (str, dict) -> None

    util.clear()

    util.write_to_lcd(event, 0, False)
    util.write_to_lcd(data.clean_file_name(payload['error']), 1, False)


def on_analysys_event(event, payload):
    # type (str, dict) -> None

    if event is 'MetadataAnalysisStarted':
        util.write_to_lcd("Started Analysis", 0)
        util.write_to_lcd(data.clean_file_name(payload['name']), 1)

    elif event is 'MetadataAnalysisFinished':

        util.write_to_lcd("Analysis Finish", 0)
        util.write_to_lcd(data.clean_file_name(payload['name']), 1)


def on_slicing_event(event, payload):
    # type (str, dict) -> None

    util.write_to_lcd(data.clean_file_name(payload['stl']), 1)

    if event is 'SlicingDone':
        minute = int(math.floor(payload['time'] / 60))
        second = int(math.floor(payload['time']) % 60)
        text = event + " {}:{}".format(minute, second)
        if len(text) > 16:
            text = text.replace(' ', '')
        util.write_to_lcd(text, 0)
        return

    if event is 'SlicingStarted' and payload['progressAvailable']:
        data.fileName = data.clean_file_name(payload['stl'])

    util.write_to_lcd(event, 0)


def on_progress_event(event, payload):
    # type (str, dict) -> None

    global _progress
    global _name
    _progress = payload['progress']
    _name = payload['name']

    switcher = {
        0: ' ',
        1: data.perc2,
        2: data.perc4,
        3: data.perc6,
        4: data.perc8,
        5: data.perc10
    }

    bar = data.perc10 * int(round(_progress / 10))
    bar += switcher[(_progress % 10) / 2]
    bar += ' ' * (10 - len(bar))

    progress_bar = "[{}] {}%".format(bar, str(_progress))

    util.write_to_lcd(_name, 0)
    util.write_to_lcd(progress_bar, 1)


def on_time_left_event(event, payload):

    util.write_to_lcd("Left: " + format_time(payload['timeLeft']), 1)


def on_time_event(event, payload):

    util.write_to_lcd("Time: " + format_time(payload['time']), 1)


def format_time(seconds):
    hours = int(math.floor(seconds / 3600))
    minutes = int(math.floor(seconds / 60) % 60)
    return "{} h,{} m".format(hours, minutes)


def on_event(eventManager, event, payload):
    # type (SynchronousEventQueue, str, dict) -> None
    """
    Can not be called asynchronously.  To protect from asynchronous
    calls, use the SynchronousEventQueue class
    """
    # self._logger.info("Processing Event: {}".format(event))

    # Make sure the lcd is enabled for the event
    util.light(True)

    if 'onnect' in event:
        on_connect_event(event, payload)
    elif event is 'Error':
        on_error_event(event, payload)
    elif 'Print' in event:
        on_print_event(event, payload)
    elif 'Anal' in event:
        on_analysys_event(event, payload)
    elif "Slicing" in event:
        on_slicing_event(event, payload)
    elif event is 'self_progress':
        on_progress_event(event, payload)

    """ Start the next synchronous event if there are any events waiting in
    the queue """

    if not eventManager.empty():
        e = eventManager.pop()
        on_event(eventManager, e.getEvent(), e.getPayload())


class carousel:
    """
    The carousel class is a static class, so no instance should be created
    To setup the carousel, init should be called first
    to start the carousel, call timer.start(), and timer.cancel() to stop
    """

    EVENTS = ['time_left', 'time', 'progress']
    _current = 0

    interval = 30

    timer = None

    @classmethod
    def init(cls):
        cls.timer = octoprint.util.RepeatedTimer(
            cls.interval,
            cls.on_event,
            run_first=False
        )

    @classmethod
    def on_event(cls, event='carousel'):

        if cls._current >= len(cls.EVENTS):
            cls._current = 0

        event = cls.EVENTS[cls._current]

        if event is 'time_left':
            on_time_left_event(event, {
                'timeLeft': PrinterStats.get_print_time_left()})
        elif event is 'time':
            on_time_event(event, {'time': PrinterStats.get_print_time()})
        elif event is 'progress':
            on_progress_event(event, {'progress': _progress, 'name': _name})

        cls._current += 1

    @classmethod
    def interval(cls):
        return cls.interval

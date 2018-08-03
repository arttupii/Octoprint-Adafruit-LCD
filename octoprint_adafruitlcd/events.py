import math

from octoprint_adafruitlcd import data
from octoprint_adafruitlcd.data import getLogger

from octoprint_adafruitlcd import util
from octoprint_adafruitlcd import synchronousEvent

from octoprint_adafruitlcd.printerStats import PrinterStats
from octoprint_adafruitlcd.timers import carousel
from octoprint_adafruitlcd.timers import timeout


"""
All events from octoprint are implemented here

The main on_event function is still in __init__.py,
but the implementation is located in events.py

Any events called will not check if the event type
is actually correct, the event variable is used for
differentiating between more specific events
"""


def on_print_event(event, payload):
    # type (str, dict) -> None

    util.write_to_lcd(event, 0)

    if event is 'PrintDone':
        data.setEventVar('time', payload)
        data.is_printing = False
        carousel.stop()
        timeout.reset()
        util.write_to_lcd("Time: " + format_time(payload['time']), 1)
        return

    if event is 'PrintStarted':
        data.setEventVar('name', payload)
        data.is_printing = True
        carousel.start()
        timeout.timer.cancel()
        util.create_custom_progress_bar()
        data.fileName = data.clean_file_name(payload['name'])
        util.write_to_lcd(data.fileName, 1)


def on_connect_event(event, payload):
    # type (str, dict) -> None

    # write the event to the screen
    util.write_to_lcd(event, 0)
    util.write_to_lcd("", 1)


def on_error_event(event, payload):
    # type (str, dict) -> None

    util.clear()
    data.setEventVar('error', payload)

    util.write_to_lcd(event, 0, False)
    util.write_to_lcd(data.clean_file_name(payload['error']), 1, False)


def on_analysys_event(event, payload):
    # type (str, dict) -> None
    data.setEventVar('name', payload)

    if event is 'MetadataAnalysisStarted':
        util.write_to_lcd("Started Analysis", 0)
        util.write_to_lcd(data.clean_file_name(payload['name']), 1)

    elif event is 'MetadataAnalysisFinished':

        util.write_to_lcd("Analysis Finish", 0)
        util.write_to_lcd(data.clean_file_name(payload['name']), 1)


def on_slicing_event(event, payload):
    # type (str, dict) -> None

    data.setEventVar('stl', payload)
    util.write_to_lcd(data.clean_file_name(payload['stl']), 1)

    if event is 'SlicingDone':
        data.setEventVar('time', payload)
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
    data.setEventVar('progress', payload)
    data.setEventVar('name', payload)

    _progress = payload['progress']
    _name = payload['name']

    if data.is_printing and \
       carousel.EVENTS[carousel._current] is not 'self_progress':
        getLogger().info(
            "The progress bar should not be updated yet, skipping")
        return

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
    data.setEventVar('printTimeLeft', payload)

    util.write_to_lcd("Left: " + format_time(payload['printTimeLeft']), 1)


def on_time_event(event, payload):
    data.setEventVar('printTime', payload)

    util.write_to_lcd("Time: " + format_time(payload['printTime']), 1)


def format_time(seconds):
    hours = int(math.floor(seconds / 3600))
    minutes = int(math.floor(seconds / 60) % 60)
    return "{} h,{} m".format(hours, minutes)


_synchronous_events = synchronousEvent.SynchronousEventQueue()
_is_LCD_printing = False


def _on_synchronous_event(eventManager, event, payload):
    # type (SynchronousEventQueue, str, dict) -> None
    """
    Can not be called asynchronously.  To protect from asynchronous
    calls, use the SynchronousEventQueue class
    """

    # Only reset the timout timer if not printing.  The timer is disabled
    # while printing, so we should not reset it
    if not data.is_printing:
        timeout.reset()

    getLogger().info("Processing Event: {}".format(event))

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
    elif event is 'self_time_left':
        on_time_left_event(event, payload)
    elif event is 'self_time':
        on_time_event(event, payload)

    """ Start the next synchronous event if there are any events waiting in
    the queue """

    if not eventManager.empty():
        e = eventManager.pop()
        _on_synchronous_event(eventManager, e.getEvent(), e.getPayload())


def on_event(event, payload):
    # start a synchronous event if there are no events waiting to be
    # executed
    global _is_LCD_printing
    if not _is_LCD_printing:
        _is_LCD_printing = True
        getLogger().debug("starting the {event} synchronous event".format(
            event=event))
        _on_synchronous_event(_synchronous_events, event, payload)
        _is_LCD_printing = False
    else:
        getLogger().debug(("adding the {event} event to "
                          + "the synchronous event queue").format(event=event))
        e = synchronousEvent.SynchronousEvent(event, payload)
        _synchronous_events.put(e)

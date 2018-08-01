import octoprint.util

from octoprint_adafruitlcd import globalVars
from octoprint_adafruitlcd.globalVars import getLogger


EVENTS = ['self_progress', 'self_time_left', 'self_time']
_current = 0

time_interval = 30
isPrinting = False

_timer = None


def start():
    """
    Start the carousel.  This should be called once when a print starts
    """
    global _current
    global isPrinting
    _current = 0
    if isPrinting or _timer.isAlive():
        getLogger().error("Carousel is already running!  Restarting")
        _timer.cancel()
        _timer.start()
        return
    getLogger().debug("Starting print carousel")
    _timer.start()
    isPrinting = True


def stop():
    """
    Stop the carousel.  This should be called when a print stops
    """
    getLogger().debug("Stopping print carousel")
    _timer.cancel()
    global isPrinting
    isPrinting = False


def getEvent():
    # type () -> str
    """
    Get the current event
    """
    return EVENTS[_current]


def _on_event():
    global _current
    _current += 1
    if _current >= len(EVENTS):
        _current = 0

    event = getEvent()

    getLogger().info("Carousel Event: {}".format(event))

    globalVars.plugin_instance.on_event(event, globalVars.event_variables)


def _interval():
    return time_interval


def init():
    global _timer
    _timer = octoprint.util.RepeatedTimer(_interval, _on_event)

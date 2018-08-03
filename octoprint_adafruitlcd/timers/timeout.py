import octoprint.util

from octoprint_adafruitlcd import data
from octoprint_adafruitlcd.data import getLogger

from octoprint_adafruitlcd import util

time_interval = 300

timer = None

_isRunning = False


def reset():
    """
    reset the timeout timer

    Called by the timer, should not be called directly
    """
    global _isRunning
    if not _isRunning:
        _isRunning = True
        getLogger().info("reset LCD timeout - Starting the timer")

        timer.start()

        util.enable_lcd(True, True)
        util.light(True, True)
        return

    timer.reset(time_interval)
    getLogger().debug("reset LCD timeout")


def _on_cancelled():
    global _isRunning
    _isRunning = False
    getLogger().debug(
        "Timeout timer is cancelled, will no longer turn off LCD")

    setup()


def _on_timeout():
    global _isRunning
    _isRunning = False
    getLogger().info("LCD timed out, turning off")

    util.clear()
    util.enable_lcd(False)
    util.light(False)

    setup()


def setup():
    global timer
    timer = octoprint.util.ResettableTimer(time_interval, _on_timeout,
                                           on_cancelled=_on_cancelled)
    getLogger().debug("Creating timeout timer")

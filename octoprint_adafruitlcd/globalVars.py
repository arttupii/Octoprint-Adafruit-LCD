plugin_instance = None  # type: Adafruit_16x2_LCD
"""
Contains the instance of the 16x2 LCD Plugin
"""

event_variables = {}
"""
Used as a buffer for current event variables.  Anyone modifiy these and read
from them
"""


def getLogger():
    # type () -> logging.Logger
    """
    Get the logger from the current plugin instance.
    """
    global plugin_instance
    return plugin_instance._logger


def setEventVar(name, variables):
    # type (str, dict) -> None
    """
    Set an event_variable with the same name from the given dictionary

    This is the same as:

    event_variables['foo'] = variables['foo']

    :name: dict key
    :variables: a dict to set the event_variable
    """
    global event_variables
    event_variables[name] = variables[name]

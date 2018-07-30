import math

from octoprint_adafruitlcd import data


class Events:
    """
    All events from octoprint are implemented here

    The main on_event function is still in __init__.py,
    but the implementation is located in events.py

    Any events called will not check if the event type
    is actually correct, the event variable is used for
    differentiating between more specific events
    """

    def __init__(self, util):
        # type (LCDData) -> None
        self.__util = util

    def on_print_event(self, event, payload):
        # type (str, dict) -> None

        self.__util.write_to_lcd(event, 0)

        if event == 'PrintDone':
            seconds = payload['time']
            hours = int(math.floor(seconds / 3600))
            minutes = int(math.floor(seconds / 60) % 60)
            self.__util.write_to_lcd("Time: {} h,{} m".format(hours, minutes),
                                     1)
            return

        if event == 'PrintStarted':
            self.__util.create_custom_progress_bar()
            data.fileName = data.clean_file_name(payload['name'])
            self.__util.write_to_lcd(data.fileName, 1)

    def on_connect_event(self, event, payload):
        # type (str, dict) -> None

        self.__util.clear()

        # turn off the lcd
        if event == 'Disconnected':
            self.__util.light(False, True)
            self.__util.enable_lcd(False, True)
            return

        # write the event to the screen
        self.__util.write_to_lcd(event, 0, False)

    def on_error_event(self, event, payload):
        # type (str, dict) -> None

        self.__util.clear()

        self.__util.write_to_lcd(event, 0, False)
        self.__util.write_to_lcd(data.clean_file_name(payload['error']),
                                 1, False)

    def on_analysys_event(self, event, payload):
        # type (str, dict) -> None

        if event == 'MetadataAnalysisStarted':
            self.__util.write_to_lcd("Started Analysis", 0)
            self.__util.write_to_lcd(data.clean_file_name(payload['name']),
                                     1)

        elif event == 'MetadataAnalysisFinished':

            self.__util.write_to_lcd("Analysis Finish", 0)
            self.__util.write_to_lcd(data.clean_file_name(payload['name']),
                                     1)

    def on_slicing_event(self, event, payload):
        # type (str, dict) -> None

        self.__util.write_to_lcd(data.clean_file_name(payload['stl']), 1)

        if event == 'SlicingDone':
            minute = int(math.floor(payload['time'] / 60))
            second = int(math.floor(payload['time']) % 60)
            text = event + " {}:{}".format(minute, second)
            if len(text) > 16:
                text = text.replace(' ', '')
            self.__util.write_to_lcd(text, 0)
            return

        if event == 'SlicingStarted' and payload['progressAvailable']:
            data.fileName = data.clean_file_name(payload['stl'])

        self.__util.write_to_lcd(event, 0)

    def on_progress_event(self, event, payload):
        # type (str, dict) -> None

        switcher = {
            0: ' ',
            1: data.perc2,
            2: data.perc4,
            3: data.perc6,
            4: data.perc8,
            5: data.perc10
        }

        bar = data.perc10 * int(round(payload['progress'] / 10))
        bar += switcher[(payload['progress'] % 10) / 2]
        bar += ' ' * (10 - len(bar))

        progress_bar = "[{}] {}%".format(bar, str(payload['progress']))

        self.__util.write_to_lcd(payload['name'], 0)
        self.__util.write_to_lcd(progress_bar, 1)

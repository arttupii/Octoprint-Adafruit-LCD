import math

class Events:
    """
    All events from octoprint are implemented here

    The main on_event function is still in __init__.py, 
    but the implementation is located in events.py

    Any events called will not check if the event type 
    is actually correct, the event variable is used for 
    differentiating between more specific events
    """

    def __init__(self, data, util):
        # type (LCDData) -> None
        self.__data = data
        self.__util = util
    
    def on_print_event(self, event, data):
        # type (str, dict) -> None

        self.__util.write_to_lcd(event, 0)

        if event == 'PrintDone':
            seconds = data['time']
            hours = int(math.floor(seconds / 3600))
            minutes = int(math.floor(seconds / 60) % 60)
            self.__util.write_to_lcd("Time: {} h,{} m".format(hours, minutes), 1)
            return
        
        if event == 'PrintStarted':
            self.__data.fileName = self.__data.clean_file_name(data['name'])
            self.__util.write_to_lcd(self.__data.fileName, 1)


    def on_connect_event(self, event, data):
        # type (str, dict) -> None

        self.__util.clear()

        # turn off the lcd
        if event == 'Disconnected':
            self.__util.light(False, True)
            self.__util.enable_lcd(False, True)
            return
        
        # write the event to the screen
        self.__util.write_to_lcd(event, 0, False)
        

    
    def on_error_event(self, event, data):
        # type (str, dict) -> None

        self.__util.clear()

        self.__util.write_to_lcd(event, 0, False)
        self.__util.write_to_lcd(self.__data.clean_file_name(data['error']), 1, False)

    def on_analysys_event(self, event, data):
        # type (str, dict) -> None

        if event == 'MetadataAnalysisStarted':
            self.__util.write_to_lcd("Started Analysis", 0)
            self.__util.write_to_lcd(self.__data.clean_file_name(data['name']), 1)
        
        elif event == 'MetadataAnalysisFinished':

            self.__util.write_to_lcd("Analysis Finish", 0)
            self.__util.write_to_lcd(self.__data.clean_file_name(data['name']), 1)

    
    def on_slicing_event(self, event, data):
        # type (str, dict) -> None

        self.__util.write_to_lcd(self.__data.clean_file_name(data['stl']), 1)

        if event == 'SlicingDone':
            minute = int(math.floor(data['time'] / 60))
            second = int(math.floor(data['time']) % 60)
            text = event + " {}:{}".format(minute, second)
            if len(text) > 16:
                text = text.replace(' ', '')
            self.__util.write_to_lcd(text, 0)
            return

        if event == 'SlicingStarted' and data['progressAvailable']:
            self.__data.fileName = self.__data.clean_file_name(data['stl'])

        self.__util.write_to_lcd(event, 0)

        

    
    def on_progress_event(self, event, data):
        # type (str, dict) -> None
        
        switcher = {
            0: ' ',
            1: self.__data.perc2,
            2: self.__data.perc4,
            3: self.__data.perc6,
            4: self.__data.perc8,
            5: self.__data.perc10
        }

        bar = self.__data.perc10 * int(round(data['progress'] / 10))
        bar += switcher[(data['progress'] % 10) / 2]
        bar += ' ' * (10 - len(bar))
        
        progress_bar = "[{}] {}%".format(bar, str(data['progress']))

        self.__util.write_to_lcd(data['name'], 0)
        self.__util.write_to_lcd(progress_bar, 1)
    
        

import octoprint.printer


class PrinterStats(octoprint.printer.PrinterCallback):
    # http://docs.octoprint.org/en/master/modules/printer.html#octoprint.printer.PrinterCallback

    __progress_print_time = 0
    __progress_print_time_left = 0

    def on_printer_send_current_data(self, data):
        """
        Called when the internal state of the Printer Interface changes
        """
        self.__class__.__progress_print_time = data['progress']['printTime']
        self.__class__.__progress_print_time_left = \
            data['progress']['printTimeLeft']

    @classmethod
    def get_print_time(cls):
        return cls.__progress_print_time

    @classmethod
    def get_print_time_left(cls):
        return cls.__progress_print_time_left

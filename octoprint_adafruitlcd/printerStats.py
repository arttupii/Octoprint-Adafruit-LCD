import octoprint.printer

from octoprint_adafruitlcd import globalVars

from octoprint_adafruitlcd.timers import carousel


class PrinterStats(octoprint.printer.PrinterCallback):
    # http://docs.octoprint.org/en/master/modules/printer.html#octoprint.printer.PrinterCallback

    def on_printer_send_current_data(self, data):
        """
        Called when the internal state of the Printer Interface changes
        """
        # Only update the eventVariables when the printer is printing
        if carousel.isPrinting:
            globalVars.setEventVar('printTimeLeft', data['progress'])
            globalVars.setEventVar('printTime', data['progress'])

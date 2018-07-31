import octoprint.printer


class DummyPrinter:

    _callback = None

    def register_callback(self, callback):
        if isinstance(callback, octoprint.printer.PrinterCallback):
            self._callback = callback

    def is_printing(self):
        return True

    def updateData(self, time, timeleft):
        if self._callback:
            self._callback.on_printer_send_current_data(
                {'progress':
                    {'printTime': time, 'printTimeLeft': timeleft}
                 })

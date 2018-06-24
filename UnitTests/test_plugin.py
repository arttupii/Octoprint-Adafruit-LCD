import unittest

import sys
import logging
import math

#setup the imports for the unit test
sys.modules['Adafruit_CharLCD'] = __import__('UnitTestAdafruit_CharLCD')
sys.path.append('octoprint_adafruitlcd')
import __init__ as adafruitLCD

class printer():

    def is_printing(self):
        return True


class TestPlugin(unittest.TestCase):

    def getLCDText(self, text):
        # type: (TestPlugin, str) -> str
        text = text[:16]
        return text + " " * (16 - len(text))

    def getPlugin(self):
        plugin = adafruitLCD.PiprintPlugin()

        logging.basicConfig()
        plugin._logger = logging.getLogger("logging")

        # plugin._logger.setLevel(10) #debug
        # plugin._logger.setLevel(20) #info
        plugin._logger.setLevel(40) #error


        plugin._printer = printer()


        plugin.on_after_startup()

        return plugin
    
    def assertTwoLines(self, plugin, line1, line2):
        self.assertEqual(plugin._get_lcd().getLCDText(0), line1)
        self.assertEqual(plugin._get_lcd().getLCDText(1), line2)

    def test_basic_write(self):
        plugin = self.getPlugin()

        plugin._write_to_lcd("Hello World!", 0, False, 0)

        result = plugin._get_lcd_text(0)
        self.assertEqual(result, self.getLCDText("Hello World!"))
        
        result = plugin._get_lcd().getLCDText(0)
        self.assertEqual(result, self.getLCDText("Hello World!"))

    def test_events(self):
        plugin = self.getPlugin()

        # print started 
        plugin.on_event("Connected", None)

        result = plugin._get_lcd().getLCDText(0)
        self.assertEqual(result, self.getLCDText("Connected"))

        # disconected
        plugin.on_event("Disconnected", None)

        result = plugin._get_lcd().getLCDText(0)
        self.assertEqual(result, self.getLCDText(""))

        # error
        plugin.on_event("Error", {"error":"Can't Even"})
        self.assertTwoLines(plugin, self.getLCDText("Error"), self.getLCDText("Can't Even"))

        # print done
        plugin.on_event("PrintDone", {"time":451234})
        self.assertTwoLines(plugin, self.getLCDText("Print Done"), self.getLCDText("Time: 125 h,20 m"))

        #print started
        plugin.on_event("PrintStarted", {"name":"foo_bar_20180624_v2.gcode"})
        self.assertTwoLines(plugin, self.getLCDText("PrintStarted"), "foo_bar_20180624")

    def test_progress(self):
        plugin = self.getPlugin()

        plugin.on_event("PrintStarted", {"name":"foo_bar_20180624_v2.gcode"})

        plugin.on_print_progress(None, None, 37)

        result = plugin._get_lcd().getLCDText(0)
        self.assertEqual(result, "foo_bar_20180624")
        result = plugin._get_lcd().getLCDText(1)
        self.assertEqual(result, self.getLCDText("[\x05\x05\x05\x03      ] 37%"))
    
    def test_pseudo_print(self):
        plugin = self.getPlugin()

        plugin.on_event("Error", {"error":"could not connect"})
        self.assertTwoLines(plugin, self.getLCDText("Error"), self.getLCDText("could not connect"))

        plugin.on_event("Connected", None)
        self.assertTwoLines(plugin, self.getLCDText("Connected"), self.getLCDText(""))

        plugin.on_event("PrintStarted", {"name":"foobar"})
        self.assertTwoLines(plugin, self.getLCDText("PrintStarted"), self.getLCDText("foobar"))

        for i in range(1, 100):
            plugin.on_print_progress(None, None, i)

            switcher = {
                1: "\x01",
                2: "\x02",
                3: "\x03",
                4: "\x04",
                5: "\x05"
            }
            filler = "\x05" * int(round(i / 10)) + switcher.get((i % 10) / 2, " ")
            spaces = " " * (10 - len(filler))
            self.assertTwoLines(plugin, self.getLCDText("foobar"), self.getLCDText("[{}{}] {}%".format(filler, spaces, str(i))))
    
        plugin.on_event("PrintDone", {"time":123456})
        self.assertTwoLines(plugin, self.getLCDText("Print Done"), self.getLCDText("Time: 34 h,17 m"))



        




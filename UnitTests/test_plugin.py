import unittest

import sys
import logging
import math

#setup the imports for the unit test
sys.modules['Adafruit_CharLCD'] = __import__('dummyLCD')
sys.path.append('octoprint_adafruitlcd')
import __init__ as adafruitLCD

import dummyLCD as LCD

class printer():

    def is_printing(self):
        return True


class TestPlugin(unittest.TestCase):

    def getLCDText(self, text):
        # type: (TestPlugin, str) -> str
        text = text[:16]
        return text + " " * (16 - len(text))

    def getPlugin(self):
        plugin = adafruitLCD.Adafruit_16x2_LCD()

        logging.basicConfig()
        plugin._logger = logging.getLogger("logging")

        # plugin._logger.setLevel(10) #debug
        # plugin._logger.setLevel(20) #info
        plugin._logger.setLevel(40) #error


        plugin._printer = printer()


        plugin.on_startup(None, None)
        plugin.on_after_startup()

        return plugin
    
    def getLCD(self, plugin):
        return plugin._Adafruit_16x2_LCD__lcd
    
    def getLCDBuffer(self, plugin, row):
        return plugin._Adafruit_16x2_LCD__current_lcd_text[row]

    def assertTwoLines(self, plugin, line1, line2):
        self.assertEqual(self.getLCD(plugin).getLCDText(0), line1)
        self.assertEqual(self.getLCD(plugin).getLCDText(1), line2)

    def test_basic_write(self):
        plugin = self.getPlugin()

        plugin._write_to_lcd("Hello World!", 0, True, 0)

        result = self.getLCDBuffer(plugin, 0)
        self.assertEqual(result, self.getLCDText("Hello World!"))
        
        result = self.getLCD(plugin).getLCDText(0)
        self.assertEqual(result, self.getLCDText("Hello World!"))

    def test_events(self):
        plugin = self.getPlugin()

        # print started 
        plugin.on_event("Connected", None)
        self.assertTwoLines(plugin, self.getLCDText("Connected"), self.getLCDText(""))

        # stupid event
        plugin.on_event("aslkdj;", None)
        self.assertTwoLines(plugin, self.getLCDText("Connected"), self.getLCDText(""))

        # disconected
        plugin.on_event("Disconnected", None)
        self.assertTwoLines(plugin, self.getLCDText(""), self.getLCDText(""))

        # error
        plugin.on_event("Error", {"error":"Can't Even"})
        self.assertTwoLines(plugin, self.getLCDText("Error"), self.getLCDText("Can't Even"))

        # print done
        plugin.on_event("PrintDone", {"time":451234})
        self.assertTwoLines(plugin, self.getLCDText("PrintDone"), self.getLCDText("Time: 125 h,20 m"))

        #print started
        plugin.on_event("PrintStarted", {"name":"foo_bar_20180624_v2.gcode"})
        self.assertTwoLines(plugin, self.getLCDText("PrintStarted"), "foo_bar_20180624")

        #analysis
        plugin.on_event("MetadataAnalysisFinished", {"name":"20180625_foo_bar_v3.gco"})
        self.assertTwoLines(plugin, self.getLCDText("Analysis Finish"), "20180625_foo_bar")

        #paused mid print
        plugin.on_print_progress(None, None, 42)
        plugin.on_event("PrintPaused", None)
        self.assertTwoLines(plugin, self.getLCDText("PrintPaused"), "[====\x01     ] 42%")

        #slicing done
        plugin.on_event("SlicingDone", {"stl":"foo_bar_v4_20180626.stl", "time":123.354})
        self.assertTwoLines(plugin, self.getLCDText("SlicingDone 2:3"), "foo_bar_v4_20180")



    def test_progress(self):
        plugin = self.getPlugin()

        plugin.on_event("PrintStarted", {"name":"foo_bar_20180624_v2.gcode"})

        plugin.on_print_progress(None, None, 37)

        result = self.getLCD(plugin).getLCDText(0)
        self.assertEqual(result, "foo_bar_20180624")
        result = self.getLCD(plugin).getLCDText(1)
        self.assertEqual(result, self.getLCDText("[===\x03      ] 37%"))
    
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
                5: "="
            }
            filler = switcher[5] * int(round(i / 10)) + switcher.get((i % 10) / 2, " ")
            spaces = " " * (10 - len(filler))
            self.assertTwoLines(plugin, self.getLCDText("foobar"), self.getLCDText("[{}{}] {}%".format(filler, spaces, str(i))))
    
        plugin.on_event("PrintDone", {"time":123456})
        self.assertTwoLines(plugin, self.getLCDText("PrintDone"), self.getLCDText("Time: 34 h,17 m"))

    def test_led(self):
        plugin = self.getPlugin()

        plugin.on_event("Connected", None)

        result = self.getLCD(plugin).getBacklight()
        self.assertEqual(result, True)

        plugin.on_event("Disconnected", None)

        result = self.getLCD(plugin).getBacklight()
        self.assertEqual(result, False)

        plugin.on_event("asld;kfj", None)

        result = self.getLCD(plugin).getBacklight()
        self.assertEqual(result, False)
        




        




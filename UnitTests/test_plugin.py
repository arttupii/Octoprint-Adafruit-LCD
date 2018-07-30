import unittest

import sys
import logging
import math

import threading

# setup the imports for the unit test
sys.modules['Adafruit_CharLCD'] = __import__('dummyLCD')
import octoprint_adafruitlcd as adafruitLCD

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
        plugin._logger.setLevel(40)  # error

        plugin._printer = printer()

        plugin.on_startup(None, None)
        plugin.on_after_startup()

        return plugin

    def getLCD(self, plugin):
        return adafruitLCD.data.lcd

    def getLCDBuffer(self, plugin, row):
        return adafruitLCD.util._current_lcd_text[row]

    def assertTwoLines(self, plugin, line1, line2):
        self.assertEqual(self.getLCD(plugin).getLCDText(0), line1)
        self.assertEqual(self.getLCD(plugin).getLCDText(1), line2)

    def test_basic_write(self):
        plugin = self.getPlugin()

        adafruitLCD.util.write_to_lcd("Hello World!", 0, True, 0)

        result = self.getLCDBuffer(plugin, 0)
        self.assertEqual(result, self.getLCDText("Hello World!"))

        result = self.getLCD(plugin).getLCDText(0)
        self.assertEqual(result, self.getLCDText("Hello World!"))

    def test_events(self):
        plugin = self.getPlugin()

        # print started
        plugin.on_event("Connected", None)
        self.assertTwoLines(plugin, self.getLCDText("Connected"),
                            self.getLCDText(""))

        # stupid event
        plugin.on_event("aslkdj;", None)
        self.assertTwoLines(plugin, self.getLCDText("Connected"),
                            self.getLCDText(""))

        # disconected
        plugin.on_event("Disconnected", None)
        self.assertTwoLines(plugin, self.getLCDText(""), self.getLCDText(""))

        # error
        plugin.on_event("Error", {"error": "Can't Even"})
        self.assertTwoLines(plugin, self.getLCDText("Error"),
                            self.getLCDText("Can't Even"))

        # print done
        plugin.on_event("PrintDone", {"time": 451234})
        self.assertTwoLines(plugin, self.getLCDText("PrintDone"),
                            self.getLCDText("Time: 125 h,20 m"))

        # print started
        plugin.on_event("PrintStarted",
                        {"name": "foo_bart_2018-06-24_v2.gcode"})
        self.assertTwoLines(plugin, self.getLCDText("PrintStarted"),
                            self.getLCDText("FooBartV2"))

        # analysis
        plugin.on_event("MetadataAnalysisFinished",
                        {"name": "20180625_foo_bar_v3.gco"})
        self.assertTwoLines(plugin, self.getLCDText("Analysis Finish"),
                            "20180625FooBarV3")

        # paused mid print
        plugin.on_print_progress(None, None, 42)
        plugin.on_event("PrintPaused", None)
        self.assertTwoLines(plugin, self.getLCDText("PrintPaused"),
                            "[====\x01     ] 42%")

        # slicing done
        plugin.on_event("SlicingDone", {"stl": "foo_bar_v4_20180626.stl",
                        "time": 123.354})
        self.assertTwoLines(plugin, self.getLCDText("SlicingDone 2:3"),
                            "FooBarV420180626")

        # slicing started
        plugin.on_event("SlicingStarted", {"stl": "foo_bar_201806262_v4.stl",
                        "progressAvailable": True})
        self.assertTwoLines(plugin, self.getLCDText("SlicingStarted"),
                            self.getLCDText("FooBarV4"))

        # slicing percentage
        plugin.on_slicing_progress("foo", "bar", "fee", "fi", "fo", 34)
        self.assertTwoLines(plugin, self.getLCDText("FooBarV4"),
                            "[===\x02      ] 34%")

    def test_progress(self):
        plugin = self.getPlugin()

        plugin.on_event("PrintStarted",
                        {"name": "foo_bar_2018-06-24_v2.gcode"})

        plugin.on_print_progress(None, None, 37)

        result = self.getLCD(plugin).getLCDText(0)
        self.assertEqual(result, "FooBar20180624V2")
        result = self.getLCD(plugin).getLCDText(1)
        self.assertEqual(result, self.getLCDText("[===\x03      ] 37%"))

    def test_pseudo_print(self):
        plugin = self.getPlugin()

        plugin.on_event("Error", {"error": "could not connect"})
        result = self.getLCD(plugin).getEnabled()
        self.assertEqual(result, True)
        self.assertTwoLines(plugin, self.getLCDText("Error"),
                            self.getLCDText("CouldNotConnect"))

        plugin.on_event("Connected", None)
        result = self.getLCD(plugin).getEnabled()
        self.assertEqual(result, True)
        self.assertTwoLines(plugin, self.getLCDText("Connected"),
                            self.getLCDText(""))

        plugin.on_event("PrintStarted", {"name": "foobar"})
        result = self.getLCD(plugin).getEnabled()
        self.assertEqual(result, True)
        self.assertTwoLines(plugin, self.getLCDText("PrintStarted"),
                            self.getLCDText("foobar"))

        for i in range(1, 100):
            plugin.on_print_progress(None, None, i)
            result = self.getLCD(plugin).getEnabled()
            self.assertEqual(result, True)

            switcher = {
                1: "\x01",
                2: "\x02",
                3: "\x03",
                4: "\x04",
                5: "="
            }
            filler = switcher[5] * int(round(i / 10)) \
                + switcher.get((i % 10) / 2, " ")
            spaces = " " * (10 - len(filler))
            self.assertTwoLines(plugin, self.getLCDText("foobar"),
                                self.getLCDText("[{}{}] {}%".format(
                                    filler, spaces, str(i))))

        plugin.on_event("PrintDone", {"time": 123456})
        result = self.getLCD(plugin).getEnabled()
        self.assertEqual(result, True)
        self.assertTwoLines(plugin, self.getLCDText("PrintDone"),
                            self.getLCDText("Time: 34 h,17 m"))

        plugin.on_event("Disconnected", None)
        result = self.getLCD(plugin).getEnabled()
        self.assertEqual(result, False)

    def test_led(self):
        plugin = self.getPlugin()

        plugin.on_event("Connected", None)

        result = self.getLCD(plugin).getBacklight()
        self.assertEqual(result, True)
        result = self.getLCD(plugin).getEnabled()
        self.assertEqual(result, True)

        plugin.on_event("Disconnected", None)

        result = self.getLCD(plugin).getBacklight()
        self.assertEqual(result, False)
        result = self.getLCD(plugin).getEnabled()
        self.assertEqual(result, False)

        plugin.on_event("asld;kfj", None)

        result = self.getLCD(plugin).getBacklight()
        self.assertEqual(result, False)
        result = self.getLCD(plugin).getEnabled()
        self.assertEqual(result, False)

    def test_string_minify(self):
        plugin = self.getPlugin()

        result = adafruitLCD.data.clean_file_name("hello.gcode")
        self.assertEqual(result, "hello.gcode")

        result = adafruitLCD.data.clean_file_name(
            "hello_what_are_do.gcode")
        self.assertEqual(result, "HelloWhatAreDo")

        result = adafruitLCD.data.clean_file_name(
            "06302018-print123.gcode")
        self.assertEqual(result, "06302018Print123")

        result = adafruitLCD.data.clean_file_name(
            "06302018-print_two123.gcode")
        self.assertEqual(result, "PrintTwo123")

        result = adafruitLCD.data.clean_file_name(
            "asdf_FooBar_cheeseGrinder.gcode")
        self.assertEqual(result, "AsdfFooBarCheese")

        result = adafruitLCD.data.clean_file_name(
            "FooBar_cheeseGrinderv3.gcode")
        self.assertEqual(result, "FooBarCheeseV3")

    def test_asynchronous_events(self):
        plugin = self.getPlugin()

        thread1 = EventThread(plugin, "PrintStarted",
                              {"name": "foo_bar_cheese_2018-06-24_v2.gcode"})
        thread2 = EventThread(plugin, "self_progress",
                              {"progress": 24, 'name': "FooBarCheeseV2"})

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        self.assertTwoLines(plugin, self.getLCDText("FooBarCheeseV2"),
                            "[==\x02       ] 24%")


class EventThread(threading.Thread):

    def __init__(self, plugin, event, payload):
        # type (Adafruit_16x2_LCD, str, dict) -> None
        super(EventThread, self).__init__()
        self.plugin = plugin
        self.event = event
        self.payload = payload

    def run(self):
        self.plugin.on_event(self.event, self.payload)

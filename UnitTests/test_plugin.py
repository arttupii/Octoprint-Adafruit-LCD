import unittest

import sys
import logging
import math

import threading

# setup the imports for the unit test
sys.modules['Adafruit_CharLCD'] = __import__('dummyLCD')
import octoprint_adafruitlcd as adafruitLCD

import dummyLCD as LCD

import pluginUtil


class TestPlugin(unittest.TestCase):

    def assertTwoLines(self, line1, line2):
        self.assertEqual(pluginUtil.getLCD().getLCDText(0), line1)
        self.assertEqual(pluginUtil.getLCD().getLCDText(1), line2)

    def test_basic_write(self):
        plugin = pluginUtil.getPlugin()

        adafruitLCD.util.write_to_lcd("Hello World!", 0, True, 0)

        result = pluginUtil.getLCD().getLCDText(0)
        self.assertEqual(result, pluginUtil.getLCDText("Hello World!"))

        result = pluginUtil.getLCD().getLCDText(0)
        self.assertEqual(result, pluginUtil.getLCDText("Hello World!"))

    def test_events(self):
        plugin = pluginUtil.getPlugin()

        # print started
        plugin.on_event("Connected", None)
        self.assertTwoLines(pluginUtil.getLCDText("Connected"),
                            pluginUtil.getLCDText(""))

        # stupid event
        plugin.on_event("aslkdj;", None)
        self.assertTwoLines(pluginUtil.getLCDText("Connected"),
                            pluginUtil.getLCDText(""))

        # disconected
        plugin.on_event("Disconnected", None)
        self.assertTwoLines(pluginUtil.getLCDText(""),
                            pluginUtil.getLCDText(""))

        # error
        plugin.on_event("Error", {"error": "Can't Even"})
        self.assertTwoLines(pluginUtil.getLCDText("Error"),
                            pluginUtil.getLCDText("Can't Even"))

        # print started
        plugin.on_event("PrintStarted",
                        {"name": "foo_bart_2018-06-24_v2.gcode"})
        self.assertTwoLines(pluginUtil.getLCDText("PrintStarted"),
                            pluginUtil.getLCDText("FooBartV2"))

        # print done
        plugin.on_event("PrintDone", {"time": 451234})
        self.assertTwoLines(pluginUtil.getLCDText("PrintDone"),
                            pluginUtil.getLCDText("Time: 125 h,20 m"))

        # analysis
        plugin.on_event("MetadataAnalysisFinished",
                        {"name": "20180625_foo_bar_v3.gco"})
        self.assertTwoLines(pluginUtil.getLCDText("Analysis Finish"),
                            "20180625FooBarV3")

        # paused mid print
        plugin.on_print_progress(None, None, 42)
        plugin.on_event("PrintPaused", None)
        self.assertTwoLines(pluginUtil.getLCDText("PrintPaused"),
                            "[====\x01     ] 42%")

        # slicing done
        plugin.on_event("SlicingDone", {"stl": "foo_bar_v4_20180626.stl",
                        "time": 123.354})
        self.assertTwoLines(pluginUtil.getLCDText("SlicingDone 2:3"),
                            "FooBarV420180626")

        # slicing started
        plugin.on_event("SlicingStarted", {"stl": "foo_bar_201806262_v4.stl",
                        "progressAvailable": True})
        self.assertTwoLines(pluginUtil.getLCDText("SlicingStarted"),
                            pluginUtil.getLCDText("FooBarV4"))

        # slicing percentage
        plugin.on_slicing_progress("foo", "bar", "fee", "fi", "fo", 34)
        self.assertTwoLines(pluginUtil.getLCDText("FooBarV4"),
                            "[===\x02      ] 34%")

    def test_progress(self):
        plugin = pluginUtil.getPlugin()

        plugin.on_event("PrintStarted",
                        {"name": "foo_bar_2018-06-24_v2.gcode"})

        plugin.on_print_progress(None, None, 37)

        self.assertTwoLines("FooBar20180624V2",
                            pluginUtil.getLCDText("[===\x03      ] 37%"))

    def test_pseudo_print(self):
        plugin = pluginUtil.getPlugin()

        plugin.on_event("Error", {"error": "could not connect"})
        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, True)
        self.assertTwoLines(pluginUtil.getLCDText("Error"),
                            pluginUtil.getLCDText("CouldNotConnect"))

        plugin.on_event("Connected", None)
        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, True)
        self.assertTwoLines(pluginUtil.getLCDText("Connected"),
                            pluginUtil.getLCDText(""))

        plugin.on_event("PrintStarted", {"name": "foobar"})
        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, True)
        self.assertTwoLines(pluginUtil.getLCDText("PrintStarted"),
                            pluginUtil.getLCDText("foobar"))

        for i in range(1, 100):
            plugin.on_print_progress(None, None, i)
            result = pluginUtil.getLCD().getEnabled()
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
            self.assertTwoLines(pluginUtil.getLCDText("foobar"),
                                pluginUtil.getLCDText("[{}{}] {}%".format(
                                    filler, spaces, str(i))))

        plugin.on_event("PrintDone", {"time": 123456})
        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, True)
        self.assertTwoLines(pluginUtil.getLCDText("PrintDone"),
                            pluginUtil.getLCDText("Time: 34 h,17 m"))

        plugin.on_event("Disconnected", None)
        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, False)

    def test_led(self):
        plugin = pluginUtil.getPlugin()

        plugin.on_event("Connected", None)

        result = pluginUtil.getLCD().getBacklight()
        self.assertEqual(result, True)
        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, True)

        plugin.on_event("Disconnected", None)

        result = pluginUtil.getLCD().getBacklight()
        self.assertEqual(result, False)
        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, False)

        plugin.on_event("asld;kfj", None)

        result = pluginUtil.getLCD().getBacklight()
        self.assertEqual(result, False)
        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, False)

    def test_string_minify(self):
        plugin = pluginUtil.getPlugin()

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
        plugin = pluginUtil.getPlugin()

        thread1 = EventThread(plugin, "PrintStarted",
                              {"name": "foo_bar_cheese_2018-06-24_v2.gcode"})
        thread2 = EventThread(plugin, "self_progress",
                              {"progress": 24, 'name': "FooBarCheeseV2"})

        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()

        self.assertTwoLines(pluginUtil.getLCDText("FooBarCheeseV2"),
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

import unittest
import time

import test_plugin

import pluginUtil

import octoprint_adafruitlcd as adafruitLCD

import dummyLCD as LCD


class TestCarousel(unittest.TestCase):

    def assertTwoLines(self, line1, line2):
        self.assertEqual(pluginUtil.getLCD().getLCDText(0), line1)
        self.assertEqual(pluginUtil.getLCD().getLCDText(1), line2)

    def test_print(self):
        plugin = pluginUtil.getPlugin()

        adafruitLCD.events.carousel.interval = 1

        plugin.on_event('PrintStarted', {'name': 'foo.gcode'})

        plugin.on_print_progress(None, None, 1)

        self.assertTwoLines(pluginUtil.getLCDText('foo.gcode'),
                            '[          ] 1% ')

        pluginUtil.printer.updateData(90, 120)

        time.sleep(1.5)

        self.assertTwoLines(pluginUtil.getLCDText('foo.gcode'),
                            pluginUtil.getLCDText('Left: 0 h,2 m'))

        time.sleep(1)

        self.assertTwoLines(pluginUtil.getLCDText('foo.gcode'),
                            pluginUtil.getLCDText('Time: 0 h,1 m'))

        time.sleep(1)

        self.assertTwoLines(pluginUtil.getLCDText('foo.gcode'),
                            '[          ] 1% ')

        plugin.on_event('PrintDone', {'time': 120})

        time.sleep(2)

        self.assertTwoLines(pluginUtil.getLCDText('PrintDone'),
                            pluginUtil.getLCDText('Time: 0 h,2 m'))

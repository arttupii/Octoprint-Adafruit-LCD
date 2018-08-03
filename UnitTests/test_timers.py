import unittest
import time

import test_plugin

import pluginUtil

import octoprint_adafruitlcd as adafruitLCD

import dummyLCD as LCD


class TestTimers(unittest.TestCase):

    def assertTwoLines(self, line1, line2):
        self.assertEqual(pluginUtil.getLCD().getLCDText(0), line1)
        self.assertEqual(pluginUtil.getLCD().getLCDText(1), line2)

    def test_carousel(self):
        plugin = pluginUtil.getPlugin()

        t = 1

        adafruitLCD.timers.carousel.time_interval = t

        plugin.on_event('PrintStarted', {'name': 'foo.gcode'})

        plugin.on_print_progress(None, None, 1)

        self.assertTwoLines(pluginUtil.getLCDText('foo.gcode'),
                            '[          ] 1% ')

        pluginUtil.printer.updateData(90, 120)

        time.sleep(1.5 * t)

        self.assertTwoLines(pluginUtil.getLCDText('foo.gcode'),
                            pluginUtil.getLCDText('Left: 0 h,2 m'))

        time.sleep(1 * t)

        self.assertTwoLines(pluginUtil.getLCDText('foo.gcode'),
                            pluginUtil.getLCDText('Time: 0 h,1 m'))

        time.sleep(1 * t)

        self.assertTwoLines(pluginUtil.getLCDText('foo.gcode'),
                            '[          ] 1% ')

        plugin.on_event('PrintDone', {'time': 120})

        time.sleep(2)

        self.assertTwoLines(pluginUtil.getLCDText('PrintDone'),
                            pluginUtil.getLCDText('Time: 0 h,2 m'))

        adafruitLCD.timers.carousel.time_interval = 30

        plugin.on_shutdown()

    def test_timeout(self):
        plugin = pluginUtil.getPlugin()

        t = 1

        adafruitLCD.timers.timeout.time_interval = t

        plugin.on_event('PrintStarted', {'name': 'foo.gcode'})

        time.sleep(1.5 * t)

        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, True)
        result = pluginUtil.getLCD().getBacklight()
        self.assertEqual(result, True)

        plugin.on_event('PrintDone', {'time': 120})

        adafruitLCD.timers.timeout.timer.join()

        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, False)
        result = pluginUtil.getLCD().getBacklight()
        self.assertEqual(result, False)

        plugin.on_event('Connected', None)

        result = pluginUtil.getLCD().getEnabled()
        self.assertEqual(result, True)
        result = pluginUtil.getLCD().getBacklight()
        self.assertEqual(result, True)

        adafruitLCD.timers.carousel.time_interval = 300

        plugin.on_shutdown()

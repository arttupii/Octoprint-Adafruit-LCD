import unittest
import dummyLCD as LCD


class TestWrite(unittest.TestCase):

    def get_lcd(self):
        return LCD.Adafruit_CharLCDPlate()

    def test_write(self):
        lcd = self.get_lcd()

        lcd.write8(ord('A'), True)

        result = lcd.getLCDText(0)
        self.assertEqual(result, "A               ")

    def test_print(self):
        lcd = self.get_lcd()

        lcd.message("Hello World!")

        result = lcd.getLCDText(0)
        self.assertEqual(result, "Hello World!    ")

    def test_cursor(self):
        lcd = self.get_lcd()

        lcd.set_cursor(15, 0)
        lcd.write8(ord("B"), True)

        result = lcd.getLCDText(0)
        self.assertEqual(result, "               B")

    def test_newline(self):
        lcd = self.get_lcd()

        lcd.message("1234567890123456\nHello World")

        result = lcd.getLCDText(0)
        self.assertEqual(result, "1234567890123456")
        result = lcd.getLCDText(1)
        self.assertEqual(result, "Hello World     ")

    def test_reverseText(self):
        lcd = self.get_lcd()

        lcd.set_cursor(15, 0)
        lcd.set_right_to_left()

        lcd.message("Hello World")

        result = lcd.getLCDText(0)
        self.assertEqual(result, "     dlroW olleH")

    def test_led(self):
        lcd = self.get_lcd()

        lcd.set_backlight(True)

        result = lcd.getBacklight()
        self.assertEqual(result, True)

        lcd.set_backlight(False)

        result = lcd.getBacklight()
        self.assertEqual(result, False)

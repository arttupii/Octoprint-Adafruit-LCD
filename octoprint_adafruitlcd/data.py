import re

class LCDData:
    """
    Holds global data for the plugin, 
    as well as some global functions
    """

    def __init__(self, lcd):
        # type (Adafruit_CharLCD)
        self.perc2 = unichr(1)
        self.perc4 = unichr(2)
        self.perc6 = unichr(3)
        self.perc8 = unichr(4)
        self.perc10 = '='

        self.lcd = lcd

        self.fileName = ""

        self.lcd_width = 16
    
    
    def special_chars_to_num(self, string):
        #type (str) -> str
        """
        Convert special characters that the LCD uses to numbers in the format '#0' or '#5'

        The range is 0 to 7 since the LCD can only store 8 special characters
        :param string: string to convert
        """
        for ch in range(0, 8):
            if unichr(ch) in string:
                string = string.replace(unichr(ch), "#{}".format(ch))
        return string
    
    def get_diff(self, str1, str2):
        #type (str, str) -> list
        """
        Get the indexes for each difference in the two strings.  The two strings 
        don't have to be the same size
        :param str1: string 1
        :param str2: string 2
        """
        return [i for i in xrange(min(len(str1), len(str2))) if str1[i] != str2[i]]

    def clean_file_name(self, name):
        #type (str) -> str
        """
        Simplify the file names to fit in the lcd screen.
        It makes several changes to the string until it is less than the lcd width

        1. remove extension
        2. remove spaces, underscores, dashes
        3. remove big numbers larger than 3 digits
        4. remove trailing words, (excluding version numbers: Vxxx)

        :param name: name to minify
        """

        if len(name) <= self.lcd_width:
            return name


        """ == Remove extension == """
        if name.find('.') != -1:
            name = name.split('.', 1)[0]
        
        if len(name) <= self.lcd_width:
            return name
        
        # Capitalize Version number
        words = re.findall(r'[v][\d]*', name)
        for v in words:
            name = name.replace(v, v.capitalize())
        
        """ == Remove dashes, underscores, and spaces.  Then capitalize each word == """
        words = re.findall(r'[a-zA-Z\d][^A-Z-_ ]*', name)
        name = ''.join([s.capitalize() for s in words])


        if len(name) <= self.lcd_width:
            return name

        """ == Remove big numbers == """

        # find all the numbers in the string
        numbers = re.findall(r'\d+', name)

        # remove numbers with more than 3 digits
        for n in numbers:
            if len(n) > 2 and len(name) > self.lcd_width:
                name = name.replace(n, "")
        

        if len(name) <= self.lcd_width:
            return name

        """ == remove extra words from the end == """

        # split the string into capitalized words
        words = re.findall(r'[\dA-Z][^A-Z]*', name)

        # remove words from the string until it is smaller or equal to the lcd width
        for w in reversed(words):
            if len(name) > self.lcd_width:
                # Make sure that version numbers are not messed with
                if len(re.findall(r'[V][\d]*', w)) == 0:
                    name = name.replace(w, "") 

        return name
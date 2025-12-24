from time import sleep_ms
class I2cLcd:
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_ENTRY_INC = 0x02
    LCD_ENTRY_SHIFT = 0x01
    LCD_ON_CTRL = 0x08
    LCD_ON_DISPLAY = 0x04
    LCD_ON_CURSOR = 0x02
    LCD_ON_BLINK = 0x01
    LCD_MOVE = 0x10
    LCD_MOVE_DISP = 0x08
    LCD_MOVE_RIGHT = 0x04
    LCD_FUNC = 0x20
    LCD_FUNC_4BIT = 0x00
    LCD_FUNC_2LINES = 0x08
    LCD_FUNC_5x10DOTS = 0x04

    def __init__(self, i2c, addr, rows=4, cols=20):
        self.i2c = i2c
        self.addr = addr
        self.rows = rows
        self.cols = cols
        self.backlight = 0x08
        self.init_lcd()

    def init_lcd(self):
        sleep_ms(20)
        self._send_init(0x03)
        sleep_ms(5)
        self._send_init(0x03)
        sleep_ms(1)
        self._send_init(0x03)
        self._send_init(0x02)
        self._cmd(self.LCD_FUNC | self.LCD_FUNC_4BIT | self.LCD_FUNC_2LINES)
        self._cmd(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)
        self.clear()
        self._cmd(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)

    def _send_init(self, data):
        self._send(data << 4)

    def _cmd(self, cmd):
        self._write(cmd, 0)

    def _data(self, data):
        self._write(data, 1)

    def _write(self, data, mode):
        hi = data & 0xF0
        lo = (data << 4) & 0xF0
        self._send(hi | (0x01 if mode else 0))
        self._send(lo | (0x01 if mode else 0))

    def _send(self, data):
        self.i2c.writeto(self.addr, bytes([data | self.backlight | 0x04]))  # EN=1
        sleep_ms(2)
        self.i2c.writeto(self.addr, bytes([(data | self.backlight) & ~0x04]))  # EN=0
        sleep_ms(2)

    def clear(self):
        self._cmd(self.LCD_CLR)
        sleep_ms(2)

    def home(self):
        self._cmd(self.LCD_HOME)
        sleep_ms(2)

    def backlight_on(self):
        self.backlight = 0x08
        self.i2c.writeto(self.addr, bytes([self.backlight]))

    def backlight_off(self):
        self.backlight = 0x00
        self.i2c.writeto(self.addr, bytes([self.backlight]))

    def move_to(self, row, col):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row >= self.rows:
            row = self.rows - 1
        self._cmd(0x80 | (col + row_offsets[row]))


    def putstr(self, text):
        for char in text:
            self._data(ord(char))


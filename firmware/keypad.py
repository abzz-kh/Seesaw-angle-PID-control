from machine import I2C
from time import sleep_ms

class Keypad:
    def __init__(self, i2c, address=0x20):
        self.i2c = i2c
        self.address = address
        # Define the keypad matrix (rows x columns)
        self.keypad = [
            ['1', '2', '3', 'A'],
            ['4', '5', '6', 'B'],
            ['7', '8', '9', 'C'],
            ['*', '0', '#', 'D']
        ]
        # Initialize the pins
        self.initialize_pins()

    def initialize_pins(self):
        # Initially, set all columns to HIGH and rows to HIGH
        self.pcf8574_write(0xFF)  # All columns HIGH, All rows HIGH

    def pcf8574_read(self):
        """Reads the state of all pins (row + column)."""
        return self.i2c.readfrom(self.address, 1)[0]

    def pcf8574_write(self, value):
        """Writes a value to the PCF8574 I/O expander."""
        self.i2c.writeto(self.address, bytes([value]))

    def scan_keypad(self):
        """Scan the keypad and return the key if pressed."""
        for row in range(4):
            # Set current row LOW (active)
            self.pcf8574_write(0xFF & ~(1 << row))  # 0xFF = all HIGH, ~(1<<row) makes one row LOW
            sleep_ms(10)  # Delay to allow the row to settle

            # Read the state of the columns
            pins_state = self.pcf8574_read()

            # Check if any column is LOW (indicating a key press)
            for col in range(4):
                if not (pins_state & (1 << (col + 4))):  # Column LOW = key pressed
                    # Return the corresponding key from the keypad matrix
                    return self.keypad[row][col]

        return None  # Return None if no key is pressed


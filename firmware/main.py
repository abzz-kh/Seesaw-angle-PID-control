from imu import MPU6050
from machine import Pin, I2C, PWM
from keypad import Keypad
from pico_i2c_lcd import I2cLcd
from time import sleep
from math import atan2, degrees
import struct
import sys
#import time

#functions
def pad(s, width):
    s = str(s)
    if len(s) >= width:
        return s[:width]
    return s + ' ' * (width - len(s))

def get_acc_angle_fast(ax,ay,az):
    return atan2(ay,(ax*ax + az*az)**0.5)

# --- SERIAL SENDER (Case 1 protocol) ---
def send_angle(angle):
    packet = bytearray()
    packet.append(0xAB)                     # Packet type = angle
    packet += struct.pack("<f", angle)      # 4-byte float
    sys.stdout.buffer.write(packet)


def send_desired_once(value):
    packet = bytearray()
    packet.append(0xAA)                     # Packet type = desired angle
    packet += struct.pack("<f", value)
    sys.stdout.write(packet)                # write to sys.stdout (not buffer)
    sleep(0.02) 

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
i2c1 = I2C(1, sda=Pin(10), scl=Pin(11), freq=400000)
#print("I2C0 devices found:", [hex(addr) for addr in i2c.scan()])
#print("I2C1 devices found:", [hex(addr) for addr in i2c1.scan()])
imu = MPU6050(i2c)   #gyro sensor
keypad = Keypad(i2c1, address=0x20)  # 0x20 for keypad
lcd = I2cLcd(i2c1, 0x27, 4, 20)  # 0x27 for LCD
# Setup for pins
in4 = Pin(18 , Pin.OUT)
in3 = Pin(19 , Pin.OUT)
in2 = Pin(20 , Pin.OUT)
in1 = Pin(21 , Pin.OUT)
led = Pin("LED" , Pin.OUT)
# Setup for Motors
Left_pwm = PWM(Pin(16))
Right_pwm = PWM(Pin(17))
Left_pwm.freq(1000)
Right_pwm.freq(1000)
#variables for Complementary filter setup
angle = 0.0
desired_angle = 0.0
dt = 0.01
j =0
is_negative = False
#Other variables
pid_labels = ["P", "I", "D"]
pid_values = {}
current_index = 0
number_str = ""
page_1 = 0
page_2 = 0
pid_output = 0
integral = 0
preportional = 0
derivative = 0
error = 0
Sangle =0
previous_angle = 0
# wellcome messege
lcd.backlight_on()
lcd.clear()
lcd.move_to(0, 2)
lcd.putstr("Angle PID control")
lcd.move_to(1, 0)
lcd.putstr("sup.: Dr.Bohlouri")
lcd.move_to(2, 0)
lcd.putstr("By:Khoshkho-Khaleghi")
lcd.move_to(3, 7)
lcd.putstr("1404")
sleep(5)
lcd.clear()
def get_values():
    global pid_values, current_index, number_str, page_1, page_2 , angle , pid_output
    global desired_angle, is_negative, kp, ki, kd , error , preportional , integral , derivative , j , previous_angle
    global sending_angle , Sangle
    sending_angle = 0
    error =0
    preportional = 0
    integral = 0
    derivative = 0
    angle = 0.0
    desired_angle = 0
    pid_output = 0
    dt = 0.01
    j =0
    is_negative = False
    pid_labels = ["P", "I", "D"]
    pid_values = {}
    current_index = 0
    number_str = ""
    page_1 = 0
    page_2 = 0
    previous_angle = 0
    #////////////////////////
    in1.value(0)
    in2.value(0)
    in3.value(0)
    in4.value(0)
    
    lcd.clear()
    lcd.move_to(0, 2)
    lcd.putstr("select PID mode")
    lcd.move_to(1, 0)
    lcd.putstr("A:Classic PID")
    lcd.move_to(2, 0)
    lcd.putstr("B:No Overshoot PID")
    lcd.move_to(3, 0)
    lcd.putstr("C:Custom")
    while page_1 == 0:
        pressed_key = keypad.scan_keypad()
        if pressed_key:
            if pressed_key == "A":
               pid_values[pid_labels[0]] = 2000
               pid_values[pid_labels[1]] = 3000
               pid_values[pid_labels[2]] = 700
               page_1 = 1
            elif pressed_key == "B":
               pid_values[pid_labels[0]] = 1000
               pid_values[pid_labels[1]] = 3000
               pid_values[pid_labels[2]] = 1000
               page_1 = 1
            elif pressed_key == "C":
                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr(f"Enter {pid_labels[current_index]} value:")
                
                while current_index < len(pid_labels):
                    lcd.move_to(3,0)
                    lcd.putstr("*:delete , #:confirm")
                    pressed_key = keypad.scan_keypad()

                    if pressed_key:
                        if pressed_key.isdigit():
                            if len(number_str) < 10:
                                number_str += pressed_key
                            lcd.move_to(1, 0)
                            lcd.putstr(pad(number_str, 20))
                
                        elif pressed_key == "#":  # confirm input
                            if number_str:
                                pid_values[pid_labels[current_index]] = int(number_str)
                                print(f"{pid_labels[current_index]} = {number_str}")
                                number_str = ""
                                current_index += 1
                
                                if current_index < len(pid_labels):
                                    lcd.clear()
                                    lcd.move_to(0, 0)
                                    lcd.putstr(f"Enter {pid_labels[current_index]} value:")
                                else:
                                    #lcd.clear()
                                    #lcd.putstr("All values entered!")
                                    page_1 = 1
                                    break
                
                        elif pressed_key == "*":  # clear input
                            number_str = ""
                            lcd.move_to(1, 0)
                            lcd.putstr(" " * 20)
                    sleep(0.2)
        sleep(0.2)
    # --- Display summary ---
    kp = pid_values["P"]
    ki = pid_values["I"]
    kd = pid_values["D"]
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr(f"P:{kp}")
    lcd.move_to(0,7)
    lcd.putstr(f"I:{ki}")
    lcd.move_to(0,14)
    lcd.putstr(f"D:{kd}")
    sleep(1)
    lcd.move_to(1,0)
    lcd.putstr("Enter desired angle:")
    lcd.move_to(3,0)
    lcd.putstr("*:delete , #:confirm")
    while page_2 == 0:
        pressed_key = keypad.scan_keypad()
        if pressed_key:
            if pressed_key == "D":
                is_negative = not is_negative
                display_str = ("-" if is_negative else "+") + number_str
                lcd.move_to(2, 0)
                lcd.putstr(pad(display_str, 20))
            if pressed_key.isdigit() :
                if len(number_str) < 2:
                    number_str += pressed_key
                display_str = ("-" if is_negative else "+") + number_str
                lcd.move_to(2, 0)
                lcd.putstr(pad(display_str, 20))
                
            elif pressed_key == "#":  # confirm input
                if number_str:
                    desired_angle = int(number_str)
                    if is_negative:
                        desired_angle = -desired_angle
                    #Clamp desired angle
                    if desired_angle < -35 :
                        desired_angle = -35
                    elif desired_angle > 35 :
                        desired_angle = 35
                    print(f"desired angle:{desired_angle}")
                    #------------------------------------------
                    send_desired_once(desired_angle)
                    #-------------------------------------------
                    lcd.move_to(1, 0)
                    lcd.putstr(" " * 20)
                    lcd.move_to(1, 6)
                    lcd.putstr("Angles:")
                    lcd.move_to(2, 0)
                    lcd.putstr(" " * 20)
                    lcd.move_to(2, 14)
                    lcd.putstr(f"SV:{desired_angle}")
                    lcd.move_to(3,0)
                    lcd.putstr(" " * 20)
                    lcd.move_to(3,0)
                    lcd.putstr("*:set new values")
                    number_str = ""
                    page_2 = 1
            elif pressed_key == "*":  # clear input
                            number_str = ""
                            lcd.move_to(2, 0)
                            lcd.putstr(" " * 20)
        sleep(0.2)
get_values()        
while True:
    #calculating angle in degrees 
    accel = imu.accel
    gyro = imu.gyro
    acc_angle = get_acc_angle_fast(accel.x , accel.y , accel.z)
    angle += (gyro.x * 0.0174533) * dt  # integrate gyro
    angle += 0.1 * (acc_angle - angle)  # complementary filter
    angle_deg = degrees(angle)
    
    #data
    Sangle += (gyro.x * 0.0174533) * dt
    Sangle += 0.5 * (acc_angle - Sangle)
    sending_angle = degrees(Sangle)
    send_angle(sending_angle)
    
    # PID calculating
    error = int(desired_angle) - angle_deg
    preportional = kp
    integral += error* dt
    derivative = gyro.z  #(angle_deg - previous_angle)/ dt
    pid_output = (kp * error)+(ki * integral) + (kd * derivative)
    previous_angle = angle_deg
    
    if pid_output> 5 :
        in1.value(0)
        in2.value(1)
        in3.value(0)
        in4.value(1)    
    elif pid_output< -5 :
        in1.value(1)
        in2.value(0)
        in3.value(1)
        in4.value(0)
    else :
        in1.value(0)
        in2.value(0)
        in3.value(0)
        in4.value(0) 
    
    left_pwm = int(abs(pid_output))
    right_pwm = int(abs(pid_output))

    # Clamp values
    left_pwm = max(0, min(65535, left_pwm))
    right_pwm = max(0, min(65535, right_pwm))

    Left_pwm.duty_u16(left_pwm)
    Right_pwm.duty_u16(right_pwm)
    pressed_key = keypad.scan_keypad()
    if pressed_key:
        if pressed_key == "*":
           get_values() 
    if j>3 :
        lcd.move_to(2,1)
        lcd.putstr("PV: {:6.2f}".format(angle_deg))
        j = 0    
    j = j+1
    #print(rounded_angle)
    #print(gyro.x , gyro.y , gyro.z)
    #print(accel.x,accel.y,accel.z)
    sleep(dt)


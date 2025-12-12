# Seesaw-angle-PID-control
A complete embedded Angle control system with PID methode + plotting software, using raspberry pi pico, MPU6050, 2 coreless motors, LN298
## 🎯Project Goal
Design and implement a precise angle-control system (<1° error) for a seesaw mechanism using:
- A custom PID controller
- Real-time feedback from MPU6050
- User interaction through LCD + keypad
- USB-based live plotting software for visualization & analysis

## 🛠️ Hardware Used
- **Raspberry Pi Pico**(controller)
- **MPU6050** (sensor)
- **L298N Motor Driver**(driver)
- **Coreless DC Motors** (actuators)
- **Character LCD** (20×4)
- **Keypad**

## 💻 Programming Languages & Software
- **Python** (PC-side plot application)
- **MicroPython** (embedded controller on Pico)
## ✨ Key Features
- User input of **PID values** and **setpoint angle** via LCD + keypad
- Real-time angle display on LCD
- Physical angle representation using a **mechanical pointer–protractor system**
- USB serial streaming + **Python plotter** to visualize Setpoint vs. Actual angle
- **Complementary Filter** for sensor fusion (acc + gyro)
- Two predefined control profiles:
  - **Classic mode**
  - **No-Overshoot mode**
- Stable performance with angle **error <1°**
## 📷 Project Media

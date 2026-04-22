# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
# 控制总线舵机转动例程
import time
from busservo import BusServo
import serial

uart = serial.Serial(port="COM17", baudrate=115200)

bus_servo = BusServo(uart)

if __name__ == "__main__":
    ID = 1  # 获取舵机ID
    bus_servo.run(ID, 500, 0)  # 设置舵机运行到500脉宽位置，运行时间为1000毫秒
    time.sleep(1)  # 延时1000毫秒
    bus_servo.run(ID, 1000, 0)  # 设置舵机运行到1000脉宽位置，运行时间为1000毫秒
    time.sleep(1)
    bus_servo.run(ID, 0, 0)  # 设置舵机运行到0脉宽位置，运行时间为2000毫秒
    time.sleep(2)
    bus_servo.run(ID, 500, 0)  # 设置舵机运行到500脉宽位置，运行时间为1000毫秒
    time.sleep(1)

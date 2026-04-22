# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
# 设置总线舵机ID
from busservo import BusServo

bus_servo = BusServo()

if __name__ == "__main__":
    oldID = bus_servo.get_ID(254)  # 获取舵机ID
    print("old ID:", bus_servo.get_ID(254))  # 打印舵机ID
    newID = 2  # 设置舵机ID
    bus_servo.set_ID(oldID, newID)  # 更改舵机ID
    print("new ID:", newID)  # 打印新舵机ID

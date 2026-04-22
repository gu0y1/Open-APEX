# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
# 读取总线舵机信息
from busservo import BusServo

bus_servo = BusServo()

if __name__ == "__main__":
    ID = bus_servo.get_ID(254)  # 获取舵机ID
    print("ID:", bus_servo.get_ID(254))  # 打印舵机ID
    print("Position:", bus_servo.get_position(ID))  # 获取舵机位置
    print("Vin:", bus_servo.get_vin(ID) / 1000)  # 获取舵机电压
    print("Offset:", bus_servo.get_offset(ID))  # 获取舵机偏差值
    print("Temp:", bus_servo.get_temp(ID))  # 获取舵机温度
    print("Angle_Range:", bus_servo.get_AngleRange(ID))  # 获取舵机角度限制
    print("Vin_Limit:", bus_servo.get_VinLimit(ID))  # 获取舵机电压限制,单位mV
    print("Temp_Limit:", bus_servo.get_TempLimit(ID))  # 获取舵机温度限制
    print("Load_Or_Unload:", bus_servo.get_LoadOrUnload(ID))  # 获取舵机状态

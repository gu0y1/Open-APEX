# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
import serial
import serial.tools.list_ports
import time


class PortUartMngr:
    def __init__(self):
        self.usb_port = None
        self.uart = None
        self.transport_delay = 0.0001

        self.connected = False

    def get_available_ports(self):
        """
        获取可用串口列表
        """
        ports = serial.tools.list_ports.comports()
        available_ports = []
        for port, desc, hwid in sorted(ports):
            # print(port, desc, hwid)
            available_ports.append(port)
        if available_ports:
            print("可用端口:")
            for port in available_ports:
                print(port)
            return available_ports
        else:
            print("未找到可用端口")
            return None

    def connect_serial(self, usb_port_name, baudrate=921600):
        """
        连接串口
        """
        if self.uart != None:
            print("串口已连接")
            return True
        else:
            try:
                self.uart = serial.Serial(port=usb_port_name, baudrate=baudrate)
                print("串口初始化成功.")
                return True
            except:
                print("串口初始化失败.")
                return False

    def disconnect_serial(self):
        """
        断开串口
        """
        if self.uart != None:
            self.uart.close()
            print("串口已断开")
            return True
        else:
            print("串口未连接")
            return False

    def send_data(self, data):
        """
        发送数据
        """
        if self.uart != None:
            self.uart.write(data)
            time.sleep(self.transport_delay)
            return True
        else:
            print("串口未连接")
            return False

    def receive_data(self, length):
        """
        接收数据
        """
        if self.uart != None:
            data = self.uart.read(length)
            return data
        else:
            print("串口未连接")
            return None

    def send_and_receive_data(self, send_data, receive_length):
        """
        发送数据并接收数据
        """
        if self.uart != None:
            self.uart.write(send_data)
            time.sleep(self.transport_delay)
            data = self.uart.read(receive_length)
            return data
        else:
            print("串口未连接")
            return None

    def send_and_receive_data_hex(self, send_data_hex, receive_length):
        """
        发送数据并接收数据
        """
        if self.uart != None:
            self.uart.write(bytes.fromhex(send_data_hex))
            time.sleep(self.transport_delay)
            data = self.uart.read(receive_length)
            return data
        else:
            print("串口未连接")
            return None

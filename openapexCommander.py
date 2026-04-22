# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
import requests
import numpy as np
import time
import zmq
from zdtstepper.zdtstepper import *
from busservo.busservo import BusServo  # 幻儿迷你舵机版本引入此库

# from scservo09 import * # sc09舵机版本引入此库


class OpenApexCommander:
    def __init__(self, pum):
        self.pum = pum
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.SNDHWM, 1)
        self.socket.bind("tcp://*:5557")
        self.url = "http://127.0.0.1:5000/get_ctraj"  # 定义服务的 URL

    def get_rot_speed(self, ja):
        js = ja[1:, :] - ja[:-1, :]
        js = np.abs(js * 5000)
        return js

    def req_ctraj(self, start, end, q0):
        data = {"s": start, "e": end, "q0": q0.tolist()}
        try:
            response = requests.post(self.url, json=data)
            if response.json()["status"] == "success":
                ja = np.array(response.json()["rst"])
                js = self.get_rot_speed(ja)
                return True, ja, js
            else:
                return False, None, None
        except Exception as e:
            print(f"Error: {e}")
            print("无法连接到服务器")
            return False, None, None

    def pub_ja(self, ja):
        for a in ja[1:, :]:
            self.socket.send_pyobj({"a": a})
            time.sleep(0.0001)

    def send2port(self, ja, js):
        for angles, speeds in zip(ja[1:, :], js):
            for i, (a, s) in enumerate(zip(angles, speeds)):
                c = round((a / 360.0) * 310464.0)
                f = 0 if c >= 0 else 1
                self.pum.send_data(Pos_Control(i + 1, f, round(s), 0, abs(c), 1, 1))
                time.sleep(0.0001)
            self.pum.send_data(Synchronous_motion(0))
            time.sleep(0.0001)

    def send2port_old(self, ja, js):
        for a, s in zip(ja[1:, :], js):
            ba3 = a[:3]
            bs3 = s[:3]
            sa3 = a[-3:]
            ss3 = s[-3:]
            # ZDT闭环步进电机转一圈需要3234个脉冲。
            # 大号减速机的减速比为60：1；小号减速机的减速比为96：1
            for bi, (ba, bs) in enumerate(zip(ba3, bs3)):
                bc = round((ba / 360.0) * 194040.0)
                bf = 0 if bc >= 0 else 1
                self.pum.send_data(
                    Pos_Control(bi + 1, bf, round(bs), 0, abs(bc), 1, 1)
                    )
                time.sleep(0.0001)
            self.pum.send_data(Synchronous_motion(0))
            time.sleep(0.0001)
            for si, (sa, ss) in enumerate(zip(sa3, ss3)):
                sc = round((sa / 360.0) * 310464.0)
                sf = 0 if sc >= 0 else 1
                self.pum.send_data(
                    Pos_Control(si + 4, sf, round(ss), 0, abs(sc), 1, 1)
                    )
                time.sleep(0.0001)
            self.pum.send_data(Synchronous_motion(0))
            time.sleep(0.0001)


if __name__ == "__main__":
    openapex_commander = OpenApexCommander()
    start = [0.2, 0.2, 0.15, 0, 0, 3.15]
    end = [0.3, 0.2, 0.15, 0, 0, 3.15]
    print(openapex_commander.req_ctraj(start, end))

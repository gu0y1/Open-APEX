# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
import subprocess
import time
import sys
import signal


proc1 = subprocess.Popen(["python", "openapexFlaskServer.py"])
time.sleep(5)
proc2 = subprocess.Popen(["python", "openapexUI.py"])


def cleanup(signum, frame):
    print("正在结束子进程...")
    # 尝试终止第一个子进程
    if proc1.poll() is None:
        proc1.terminate()
    # 尝试终止第二个子进程
    if proc2.poll() is None:
        proc2.terminate()
    sys.exit(0)


# 捕获终止信号
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

try:
    proc2.wait()  # 先等待 openapexUI.py 结束
    if proc1.poll() is None:  # 检查 openapexFlaskServer.py 是否还在运行
        proc1.terminate()  # 结束 openapexFlaskServer.py 进程
    proc1.wait()  # 等待 openapexFlaskServer.py 进程结束
except KeyboardInterrupt:
    cleanup(None, None)

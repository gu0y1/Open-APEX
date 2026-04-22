# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
from flask import Flask, request, jsonify
import numpy as np
from spatialmath import SE3
import roboticstoolbox as rtb
from ursina import distance

np.set_printoptions(precision=3, suppress=True)


class OpenApex:
    def __init__(self):
        self.gripper_length = 0.14

        self.dh_params_old = np.array(
            [
                # |  d  |  a  |  alpha  |  theta  |
                [0.0948, 0.0, 0.5 * np.pi, 0.0],
                [0.0, 0.24, np.pi, 0.5 * np.pi],
                [0.0, 0.24, np.pi, 0.5 * np.pi],
                [0.1064, 0.0, -0.5 * np.pi, -0.5 * np.pi],
                [0.0784, 0.0, 0.5 * np.pi, 0.5 * np.pi],
                [0.0364 + self.gripper_length, 0.0, 0.0, 0.5 * np.pi],
            ]
        )

        self.dh_params = np.array(
            [
                # |  d  |  a  |  alpha  |  theta  |
                [0.050 + 0.0314, 0.0, 0.5 * np.pi, 0.0],
                [0.0, 0.22, np.pi, 0.5 * np.pi],
                [0.0, 0.22, np.pi, 0.5 * np.pi],
                [0.0834, 0.0, -0.5 * np.pi, -0.5 * np.pi],
                [0.0734, 0.0, 0.5 * np.pi, 0.5 * np.pi],
                [0.0314 + self.gripper_length, 0.0, 0.0, 0.5 * np.pi],
            ]
        )
        self.joint_limits = [
            [-1.0 * np.pi, 1.0 * np.pi],  # 关节 1 的上下限
            [-0.5 * np.pi, 0.5 * np.pi],  # 关节 2 的上下限
            [-1.0 * np.pi, 1.0 * np.pi],  # 关节 3 的上下限
            [-1.0 * np.pi, 1.0 * np.pi],  # 关节 4 的上下限
            [-1.0 * np.pi, 1.0 * np.pi],  # 关节 5 的上下限
            [-2.0 * np.pi, 2.0 * np.pi],  # 关节 6 的上下限
        ]
        self.links = []
        for i, (d, a, alpha, theta) in enumerate(self.dh_params_old):
            link = rtb.RevoluteDH(
                d=d, a=a, alpha=alpha, offset=theta, qlim=self.joint_limits[i]
            )
            self.links.append(link)
        self.robot = rtb.DHRobot(self.links, name="OpenAPEX")
        self.home_ja = np.array(self.robot.q)  # array([0., 0., 0., 0., 0., 0.])

    def get_ctraj(self, start, end, q0):
        T_start = SE3.Trans(start[:3]) * SE3.RPY(start[3:6], order="xyz")
        T_end = SE3.Trans(end[:3]) * SE3.RPY(end[3:6], order="xyz")
        if T_start == T_end:
            print("起始点和目标点相同，无运动路径生成，请重新调整目标位置。")
            return False, None
        dist = distance(start[:3], end[:3])
        print(f"位移量: {dist}")
        R_rel = T_start.R.T @ T_end.R  # 相对旋转矩阵
        delta_angle = np.arccos((np.trace(R_rel) - 1) / 2)
        print(f"旋转角: {np.rad2deg(delta_angle):.2f}°")
        steps_by_dist = round(dist / 0.0002)
        steps_by_delta_angle = round(np.rad2deg(delta_angle) / 0.1)
        steps = max(steps_by_dist, steps_by_delta_angle)
        print(f"步数: {steps}")
        ct = rtb.ctraj(T_start, T_end, steps)
        ja = np.zeros((1, 6))
        pre_ja = q0
        for T_pose in ct:
            rst = self.robot.ik_LM(T_pose, q0=pre_ja, joint_limits=True, tol=1e-12)
            if rst[1]:
                pre_ja = rst[0]
                ja = np.vstack((ja, pre_ja))
            else:
                print("逆解失败并停止，请重新调整目标位置。")
                return False, None
        print("逆解完成")
        ja = np.rad2deg(ja[1:, :])
        print(f"帧数: {len(ja)}")
        return True, ja


app = Flask(__name__)

openapex = OpenApex()


@app.route("/get_ctraj", methods=["POST"])
def get_ctraj():
    try:
        data = request.get_json()
        s = data["s"]
        e = data["e"]
        q0 = data["q0"]
        _, rst = openapex.get_ctraj(start=np.array(s), end=np.array(e), q0=q0)
        if _:
            response_data = {"rst": rst.tolist(), "status": "success"}
            return jsonify(response_data)
        else:
            return jsonify({"status": "failed", "rst": None}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=False, threaded=True)

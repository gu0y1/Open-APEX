# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
import zmq
import numpy as np
from ursina import *
from ursina.shaders import lit_with_shadows_shader

Entity.default_shader = lit_with_shadows_shader


class OpenApexVisual:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.RCVHWM, 1)
        self.socket.connect("tcp://localhost:5557")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.update_tool = Entity(update=self.update, rotation_x=90)

        self.link0 = Entity(
            parent=self.update_tool, model=load_model("model/link0.glb")
        )
        self.link1 = Entity(
            parent=self.link0, model=load_model("model/link1.glb"), z=-0.050
        )
        self.link2 = Entity(
            parent=self.link1,
            model=load_model("model/link2.glb"),
            y=-0.060,
            z=-0.0448,
            rotation_x=-90,
            rotation_z=-90,
        )
        self.link3 = Entity(
            parent=self.link2,
            x=0.240,
            rotation_x=180,
            rotation_z=-90,
            model=load_model("model/link3.glb"),
        )
        self.link4 = Entity(
            parent=self.link3,
            x=0.240,
            rotation_x=180,
            z=0.0044,
            model=load_model("model/link4.glb"),
        )
        self.link5 = Entity(
            parent=self.link4,
            x=0.0364,
            z=-0.042,
            rotation_y=-90,
            rotation_z=90,
            model=load_model("model/link5.glb"),
        )
        self.link6 = Entity(
            parent=self.link5,
            x=0.0364 + 0.14,
            z=-0.042,
            rotation_y=-90,
            rotation_z=180,
            model=load_model("model/link6.glb"),
            alpha=0.5,
        )

        self.links = [
            self.link0,
            self.link1,
            self.link2,
            self.link3,
            self.link4,
            self.link5,
            self.link6,
        ]
        self.ja = np.array([0, 0, 0, 0, 0, 0])
        self.rot_xyz = np.array([0, 0, np.pi])

        self.cln_able_list = [
            [self.link3, self.link6],  # link0 0-3 0-6
            [self.link3, self.link6],  # link1 1-3 1-6
            [self.link4, self.link5, self.link6],  # link2 2-4 2-5 2-6
            [],  # link3 3-0 3-1 3-6
            [],  # link4 4-2
            [],  # link5 5-2
            [],  # link6 6-0 6-1 6-2 6-3
        ]

    def set_model_ja(self, ja):
        self.link1.rotation_z = -1.0 * ja[0]
        self.link2.rotation_z = -90 + -1.0 * ja[1]
        self.link3.rotation_z = -90 + -1.0 * ja[2]
        self.link4.rotation_z = -1.0 * ja[3]
        self.link5.rotation_z = 90 + -1.0 * ja[4]
        self.link6.rotation_z = 180 + -1.0 * ja[5]

    def get_clninfo(self, ja):
        self.set_model_ja(ja)
        for i, link in enumerate(self.links):
            if self.cln_able_list[i] == []:
                continue
            for l in self.cln_able_list[i]:
                hitinfo = link.intersects(l)
                if hitinfo.hit:
                    print("检测到碰撞，请重新调整目标位置。")
                    return True
        return False

    def get_traj_clninfo(self, ja):
        for s in ja:
            if self.get_clninfo(s):
                return True
        print("轨迹中未检测到碰撞")
        return False

    def update(self):
        if self.socket.poll(time.dt):
            msg = self.socket.recv_pyobj()
            self.ja = msg["a"]
            self.set_model_ja(self.ja)


if __name__ == "__main__":
    app = Ursina(
        title="OpenAPEX 机器人控制程序",
        borderless=False,
        fullscreen=False,
        development_mode=False,
        size=(1366, 768),
        icon="ico/box.ico",
    )

    ec = EditorCamera()
    ec.rotation_x = 30
    ec.target_z = -3

    sky = Sky()

    sun = DirectionalLight()
    sun.shadow_map_resolution = Vec2(4096 * 2, 4096 * 2)
    sun.look_at(Vec3(1, -1, 1))

    ground = Entity(
        model="plane",
        color=color.gray,
        texture="white_cube",
        texture_scale=(100, 100),
        scale=10,
        y=-0.002,
    )

    openapex_visual = OpenApexVisual()

    app.run()

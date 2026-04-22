# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
import numpy as np
from ursina import *
from ursina.prefabs.input_field import InputField


class TargetTool(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.require_key = None
        self.dragging = False
        self.delta_drag = 0
        self.start_pos = self.world_position
        self.start_offset = (0, 0, 0)
        self.step = (0.0001, 0.0001, 0.0001)
        self.plane_direction = (0, 0, 1)
        self.lock = Vec3(0, 0, 0)  # set to 1 to lock movement on any of x, y and z axes
        self.min_x, self.min_y, self.min_z = -inf, -inf, -inf
        self.max_x, self.max_y, self.max_z = inf, inf, inf
        tool_radius = 0.35
        tool_height = 1.5
        tool_dis = 1.5
        self.x_tool = Button(
            parent=self,
            model=Cone(16, tool_radius, tool_height),
            color=color.red,
            position=(tool_dis, 0, 0),
            rotation_z=90,
        )
        self.x_tool_inverse = Button(
            parent=self,
            model=Cone(16, tool_radius, tool_height),
            color=color.gray,
            position=(-tool_dis, 0, 0),
            rotation_z=-90,
        )
        self.y_tool = Button(
            parent=self,
            model=Cone(16, tool_radius, tool_height),
            color=color.green,
            position=(0, 0, tool_dis),
            rotation_x=90,
        )
        self.y_tool_inverse = Button(
            parent=self,
            model=Cone(16, tool_radius, tool_height),
            color=color.gray,
            position=(0, 0, -tool_dis),
            rotation_x=-90,
        )
        self.z_tool = Button(
            parent=self,
            model=Cone(16, tool_radius, tool_height),
            color=color.blue,
            position=(0, tool_dis, 0),
        )
        self.z_tool_inverse = Button(
            parent=self,
            model=Cone(16, tool_radius, tool_height),
            color=color.gray,
            position=(0, -tool_dis, 0),
            rotation_x=180,
        )
        self.xf_tool = Button(
            parent=self,
            model=Cylinder(16, tool_radius, tool_height),
            color=color.red,
            position=(tool_dis, 0, 0),
            rotation_z=90,
            on_click=self.face_left,
        )
        self.xf_tool_inverse = Button(
            parent=self,
            model=Cylinder(16, tool_radius, tool_height),
            color=color.gray,
            position=(-tool_dis, 0, 0),
            rotation_z=-90,
            on_click=self.face_right,
        )
        self.yf_tool = Button(
            parent=self,
            model=Cylinder(16, tool_radius, tool_height),
            color=color.green,
            position=(0, 0, tool_dis),
            rotation_x=90,
            on_click=self.face_forward,
        )
        self.yf_tool_inverse = Button(
            parent=self,
            model=Cylinder(16, tool_radius, tool_height),
            color=color.gray,
            position=(0, 0, -tool_dis),
            rotation_x=-90,
            on_click=self.face_back,
        )
        self.zf_tool = Button(
            parent=self,
            model=Cylinder(16, tool_radius, tool_height),
            color=color.blue,
            position=(0, tool_dis, 0),
            on_click=self.face_down,
        )
        self.zf_tool_inverse = Button(
            parent=self,
            model=Cylinder(16, tool_radius, tool_height),
            color=color.gray,
            position=(0, -tool_dis, 0),
            rotation_x=180,
            on_click=self.face_up,
        )
        self.vectool = Entity(
            parent=self,
            rotation_x=90,
        )
        self.vectool1 = Entity(parent=self)
        self.vectool2 = Entity(
            parent=self.vectool1, scale=10, model=load_model("model2/link6.glb")
        )
        self.rot = Vec3(0, 0, 180)
        self.inputf_x = InputField(x=0.6, y=-0.20)
        self.inputf_y = InputField(x=0.6, y=-0.25)
        self.inputf_z = InputField(x=0.6, y=-0.30)
        self.inputf_r1 = InputField(x=0.6, y=-0.35)
        self.inputf_r2 = InputField(x=0.6, y=-0.40)
        self.inputf_r3 = InputField(x=0.6, y=-0.45)

        for key, value in kwargs.items():
            if key == "collider" and value == "sphere" and self.has_ancestor(camera.ui):
                print(
                    "error: sphere colliders are not supported on Draggables in ui space."
                )
            if key == "text" or key in self.attributes:
                continue
            setattr(self, key, value)

    def face_up(self):
        self.rot = Vec3(0, 0, 0)

    def face_down(self):
        self.rot = Vec3(0, 0, 180)

    def face_left(self):
        self.rot = Vec3(0, -90, 180)

    def face_right(self):
        self.rot = Vec3(0, 90, 180)

    def face_forward(self):
        self.rot = Vec3(0, 0, 90)

    def face_back(self):
        self.rot = Vec3(0, 0, -90)

    def key_command(self, key):
        pass

    def input(self, key):
        if (
            self.x_tool.hovered or self.x_tool_inverse.hovered
        ) and key == "left mouse down":
            self.plane_direction = (0, 0, 1)
            self.lock = Vec3(0, 1, 1)
            if self.require_key == None or held_keys[self.require_key]:
                self.start_dragging()
        if (
            self.y_tool.hovered or self.y_tool_inverse.hovered
        ) and key == "left mouse down":
            self.plane_direction = (0, 1, 0)
            self.lock = Vec3(1, 1, 0)
            if self.require_key == None or held_keys[self.require_key]:
                self.start_dragging()
        if (
            self.z_tool.hovered or self.z_tool_inverse.hovered
        ) and key == "left mouse down":
            self.plane_direction = (1, 0, 0)
            self.lock = Vec3(1, 0, 1)
            if self.require_key == None or held_keys[self.require_key]:
                self.start_dragging()
        if self.dragging and key == "left mouse up":
            self.stop_dragging()

        # 按其他键盘按键执行命令
        self.key_command(key)

    def start_dragging(self):
        point = Vec3(0, 0, 0)
        if mouse.world_point:
            point = mouse.world_point
        self.start_offset = point - self.world_position
        self.dragging = True
        self.start_pos = self.world_position
        self.collision = False
        mouse._original_traverse_target = mouse.traverse_target
        if hasattr(self, "drag"):
            self.drag()

    def stop_dragging(self):
        self.dragging = False
        self.delta_drag = self.world_position - self.start_pos
        self.collision = True
        if hasattr(mouse, "_original_traverse_target"):
            mouse.traverse_target = mouse._original_traverse_target
        else:
            mouse.traverse_target = scene
        if hasattr(self, "drop"):
            self.drop()

    def drag(self):
        self.getPR()

    def drop(self):
        self.getPR()

    def getPR(self):
        pos = self.world_position
        pos[0], pos[1], pos[2] = pos[0], pos[2], pos[1]
        rot = np.deg2rad(self.rot)
        # print(pos, rot)
        return pos, rot

    def get_real_pos(self, e):
        pos = e.world_position
        pos[1], pos[2] = pos[2], pos[1]
        return pos

    def setPR(self):
        pass

    def update_inputf(self):
        pos = self.world_position
        pos[0], pos[1], pos[2] = pos[0], pos[2], pos[1]
        self.inputf_x.text = f"{pos[0]:.3f}"
        self.inputf_y.text = f"{pos[1]:.3f}"
        self.inputf_z.text = f"{pos[2]:.3f}"
        self.inputf_r1.text = f"{self.rot[0]:.3f}"
        self.inputf_r2.text = f"{self.rot[1]:.3f}"
        self.inputf_r3.text = f"{self.rot[2]:.3f}"

    def update(self):
        pos_dir = Vec3(
            held_keys["right arrow"] - held_keys["left arrow"],
            held_keys["page up"] - held_keys["page down"],
            held_keys["up arrow"] - held_keys["down arrow"],
        ).normalized()
        self.world_position += pos_dir * 0.4 * time.dt
        rot_dir = Vec3(
            -(held_keys["."] - held_keys[","]),
            -(held_keys["l"] - held_keys["j"]),
            -(held_keys["i"] - held_keys["k"]),
        ).normalized()
        self.rot += rot_dir * 100 * time.dt
        vec_rot = deepcopy(self.rot)
        vec_rot_chace = deepcopy(vec_rot)
        vec_rot_0 = -vec_rot_chace[2] + 90
        vec_rot_1 = -vec_rot_chace[1]
        vec_rot_2 = -vec_rot_chace[0]
        self.vectool.rotation = Vec3(vec_rot_0, vec_rot_1, vec_rot_2)
        self.vectool1.rotation_x = vec_rot_0
        self.vectool2.rotation_y = vec_rot_1
        if self.dragging:
            if mouse.world_point:
                if not self.lock[0]:
                    self.world_x = mouse.world_point[0] - self.start_offset[0]
                if not self.lock[1]:
                    self.world_y = mouse.world_point[1] - self.start_offset[1]
                if not self.lock[2]:
                    self.world_z = mouse.world_point[2] - self.start_offset[2]

            if self.step[0] > 0:
                hor_step = 1 / self.step[0]
                self.x = round(self.x * hor_step) / hor_step
            if self.step[1] > 0:
                ver_step = 1 / self.step[1]
                self.y = round(self.y * ver_step) / ver_step
            if self.step[2] > 0:
                dep_step = 1 / self.step[2]
                self.z = round(self.z * dep_step) / dep_step

            self.update_inputf()

        self.world_position = (
            clamp(self.x, self.min_x, self.max_x),
            clamp(self.y, self.min_y, self.max_y),
            clamp(self.z, self.min_z, self.max_z),
        )

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, value):
        if isinstance(value, (int, float, complex)):
            value = (value, value, value)
        self._step = value


if __name__ == "__main__":
    app = Ursina(
        title="位姿导航控件测试程序",
        borderless=False,
        fullscreen=False,
        development_mode=False,
        size=(1366, 768),
    )

    ec = EditorCamera()

    targetrool = TargetTool(
        parent=scene, model="sphere", scale=1, color=color.white, alpha=0.5
    )

    app.run()

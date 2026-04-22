# Author: Chen Guoyi, guoyi@comp.nus.edu.sg, NUS Computing
import threading
import numpy as np
from ursina import *
from ursina.prefabs.dropdown_menu import DropdownMenu, DropdownMenuButton
from ursina.shaders import lit_with_shadows_shader
from openapexVirtual import OpenApexVisual
from openapexTargetTool import TargetTool
from openapexCommander import *
from tools.JsonConfigMngr import JsonConfigMngr
from tools.PortUartMngr import PortUartMngr

Entity.default_shader = lit_with_shadows_shader
Text.default_font = "font/oafont.ttf"  # 字体文件路径


class TaskKeyPoint:
    def __init__(self, position, rotation, arrive_mode):
        self.position = position
        self.rotation = rotation
        self.arrive_mode = arrive_mode


class TaskSequenceManager:
    def __init__(self):
        self.taskKeyPoints = []
        self.s = Sequence()

    def add_task_keypoint(self, arrive_mode):
        print(f"添加任务关键点，到达方式为{arrive_mode}")
        sp, ep, sr, er = get_target_tool_PR()
        self.taskKeyPoints.append(TaskKeyPoint(ep, er, arrive_mode))
        self.updataTaskSequence()

    def add_task(self, sp, ep, sr, er, arrive_mode):
        d = get_movement_duration(sp, ep, sr, er)
        self.s.append(Func(task_movement, sp, ep, sr, er, arrive_mode))
        self.s.append(d)

    def updataTaskSequence(self):
        l = len(self.taskKeyPoints)
        print(f"当前任务序列长度为{l}")
        if l >= 2:
            self.add_task(
                self.taskKeyPoints[-2].position,
                self.taskKeyPoints[-1].position,
                self.taskKeyPoints[-2].rotation,
                self.taskKeyPoints[-1].rotation,
                self.taskKeyPoints[-1].arrive_mode,
            )

    def add_gripper_task(self):
        self.s.append(Func(servo.run, 1, g_slider.value, 0))
        self.s.append(0.5)

    def start_task(self):
        print("开始任务")
        self.s.start()

    def stop_task(self):
        print("停止任务")
        self.s.finish()

    def clear_tasks(self):
        self.taskKeyPoints = []
        self.s = Sequence()
        print("任务队列已清空")


if __name__ == "__main__":
    jcm = JsonConfigMngr()
    pum = PortUartMngr()
    gpum = PortUartMngr()

    app = Ursina(
        title="OpenAPEX 机器人控制程序",
        borderless=False,
        fullscreen=False,
        development_mode=False,
        size=(1366, 768),
        icon="ico/box.ico",
    )

    ec_vec = {"up": Vec3(90, 0, 0), "front": Vec3(0, 0, 0), "right": Vec3(0, -90, 0)}

    ec = EditorCamera()
    ec.rotation_x = 30
    ec.target_z = -3

    def reset_ec():
        ec.position = ec.start_position
        ec.look_at_xy(Vec2(0, 0))

    def set_ec(v):
        reset_ec()
        ec.rotation = v

    sky = Sky()

    sun = DirectionalLight()
    sun.shadow_map_resolution = Vec2(4096 * 2, 4096 * 2)
    sun.look_at(Vec3(1, -1, 1))

    ground = Entity(
        model="plane",
        color=color.gray,
        texture="white_cube",
        texture_scale=(100, 100),
        alpha=0.75,
        scale=10,
        y=-0.002,
    )
    grid = Entity(model=Grid(10, 10), rotation_x=90, color=color.gray, y=0, scale=10)

    sound = Audio(sound_file_name="test_sound.mp3", autoplay=False)
    sound.play()

    servo = None

    def connect_serial(port):
        if pum.connect_serial(port):
            jcm.update_config("port", config_value=port)

    def connect_serial_g(gport):
        global servo
        if gpum.connect_serial(gport, baudrate=115200):
            jcm.update_config("gport", config_value=gport)
            servo = BusServo(gpum.uart)

    def show_port_list(b):
        available_ports = pum.get_available_ports()
        button_dict_port_list = {}
        if available_ports != None:
            for i, p in enumerate(available_ports):
                button_dict_port_list[p] = Func(connect_serial, p)
        else:
            button_dict_port_list["无可用串口"] = Func(print, "无可用串口")
        bl_port_list = ButtonList(
            button_dict_port_list,
            font="font/oafont.ttf",
            button_height=1.5,
            popup=1,
            clear_selected_on_enable=False,
            enabled=False,
        )
        bl_port_list.enabled = b

    def show_port_list_g(b):
        available_ports = pum.get_available_ports()
        button_dict_port_list = {}
        if available_ports != None:
            for i, p in enumerate(available_ports):
                button_dict_port_list[p] = Func(connect_serial_g, p)
        else:
            button_dict_port_list["无可用串口"] = Func(print, "无可用串口")
        bl_port_list = ButtonList(
            button_dict_port_list,
            font="font/oafont.ttf",
            button_height=1.5,
            popup=1,
            clear_selected_on_enable=False,
            enabled=False,
        )
        bl_port_list.enabled = b

    ft_step = 10

    def set_ft_step(v):
        global ft_step
        ft_step = v
        print(f"微调量设置为{ft_step}度")

    def fine_tune(i, d):
        global ft_step
        v = ft_step
        pum.send_data(Pos_Control(i, d, 500, 223, abs(round(v / 360 * 310464.0)), 0, 0))
        print(f"电机{i}向{d}方向微调了{v}度")

    def set_all_0():
        pum.send_data(Reset_CurPos_To_Zero(0))
        print("所有电机记零")

    def set_all_home():
        pum.send_data(Pos_Control(0, 1, 500, 127, 0, 1, 1))
        time.sleep(0.0001)
        pum.send_data(Synchronous_motion(0))
        time.sleep(0.0001)
        openapex_r.set_model_ja(np.array([0, 0, 0, 0, 0, 0]))
        print("所有电机回零")

    def show_bl_ft(b):
        bl_ft.enabled = b

    button_dict_fine_tune = {}
    button_dict_fine_tune["微调量设置为10度"] = Func(set_ft_step, 10)
    button_dict_fine_tune["微调量设置为1度"] = Func(set_ft_step, 1)
    button_dict_fine_tune["微调量设置为0.1度"] = Func(set_ft_step, 0.1)
    button_dict_fine_tune["微调量设置为0.01度"] = Func(set_ft_step, 0.01)
    for i in range(1, 7):
        button_dict_fine_tune[f"轴{i}顺时针微调"] = Func(fine_tune, i, 1)
        button_dict_fine_tune[f"轴{i}逆时针微调"] = Func(fine_tune, i, 0)
    button_dict_fine_tune["所有电机回零"] = set_all_home
    button_dict_fine_tune["所有电机清零"] = set_all_0
    button_dict_fine_tune["退出微调"] = Func(show_bl_ft, False)
    bl_ft = ButtonList(
        button_dict_fine_tune,
        font="font/oafont.ttf",
        button_height=1.5,
        x=-0.75,
        y=0.35,
        popup=0,
        clear_selected_on_enable=False,
    )
    bl_ft.enabled = False

    def show_bl_task_editor(b):
        bl_task_editor.enabled = b

    ts_mngr = TaskSequenceManager()

    bl_task_editor = ButtonList(
        {
            "记录lin关键点": Func(ts_mngr.add_task_keypoint, "linear"),
            "记录p2p关键点": Func(ts_mngr.add_task_keypoint, "p2p"),
            "记录夹爪关键点": ts_mngr.add_gripper_task,
            "清空路径关键点": ts_mngr.clear_tasks,
            "退出路径编辑": Func(show_bl_task_editor, False),
        },
        font="font/oafont.ttf",
        button_height=1.5,
        x=-0.75,
        y=0.0,
        popup=0,
        enabled=False,
    )

    dm = DropdownMenu(
        "系统菜单",
        buttons=(
            DropdownMenu(
                "通讯设置",
                buttons=(
                    DropdownMenuButton(
                        "连接机械臂串口", on_click=Func(show_port_list, True)
                    ),
                    DropdownMenuButton(
                        "连接夹持器串口", on_click=Func(show_port_list_g, True)
                    ),
                    DropdownMenuButton("连接局域网端口"),
                ),
            ),
            DropdownMenuButton("关节微调", on_click=Func(show_bl_ft, True)),
            DropdownMenuButton("任务编辑", on_click=Func(show_bl_task_editor, True)),
            DropdownMenu(
                "视口调整",
                buttons=(
                    DropdownMenuButton("重置视口", on_click=Func(reset_ec)),
                    DropdownMenuButton("上视图", on_click=Func(set_ec, ec_vec["up"])),
                    DropdownMenuButton(
                        "前视图", on_click=Func(set_ec, ec_vec["front"])
                    ),
                    DropdownMenuButton(
                        "右视图", on_click=Func(set_ec, ec_vec["right"])
                    ),
                ),
            ),
            DropdownMenuButton(
                "退出程序",
                on_click=Func(application.quit),
            ),
        ),
    )

    openapex_v = OpenApexVisual()
    openapex_r = OpenApexVisual()

    def openapex_v_update():
        pass

    openapex_v.update_tool.update = openapex_v_update
    openapex_v.link0.visible = False

    openapex_v.link0.collider = "box"
    openapex_v.link1.collider = "box"
    openapex_v.link2.collider = "box"
    openapex_v.link3.collider = "box"
    openapex_v.link4.collider = "box"
    openapex_v.link5.collider = "box"
    openapex_v.link6.collider = "box"

    openapex_v.link0.collider.visible = True
    openapex_v.link1.collider.visible = True
    openapex_v.link2.collider.visible = True
    openapex_v.link3.collider.visible = True
    openapex_v.link4.collider.visible = True
    openapex_v.link5.collider.visible = True
    openapex_v.link6.collider.visible = True

    def get_target_tool_PR():
        sp = target_tool.get_real_pos(openapex_r.link6)
        sr = openapex_r.rot_xyz
        ep, er = target_tool.getPR()
        return sp, ep, sr, er

    def target_tool_movement(arrive_mode):
        sp, ep, sr, er = get_target_tool_PR()
        task_movement(sp, ep, sr, er, arrive_mode)

    def get_movement_duration(sp, ep, sr, er):
        _, rst_ja, rst_js = openapex_commander.req_ctraj(
            [sp[0], sp[1], sp[2], sr[0], sr[1], sr[2]],
            [ep[0], ep[1], ep[2], er[0], er[1], er[2]],
            openapex_v.ja,
        )
        duration = len(rst_ja) * 0.0125 if _ else 0
        return duration

    def task_movement(sp, ep, sr, er, arrive_mode):
        _, rst_ja, rst_js = openapex_commander.req_ctraj(
            [sp[0], sp[1], sp[2], sr[0], sr[1], sr[2]],
            [ep[0], ep[1], ep[2], er[0], er[1], er[2]],
            openapex_v.ja,
        )
        if _ and not openapex_v.get_traj_clninfo(rst_ja):
            if arrive_mode == "linear":
                max_js = np.max(rst_js)
                if max_js < 2000:
                    threading.Thread(
                        target=openapex_commander.pub_ja, args=(rst_ja,)
                    ).start()
                    threading.Thread(
                        target=openapex_commander.send2port_old,
                        args=(
                            rst_ja,
                            rst_js,
                        ),
                    ).start()
                    openapex_r.rot_xyz = er
                    target_tool.rot = np.rad2deg(er)
                else:
                    print(
                        f"最大角速度: {max_js} 超出最大角速度限制，请重新调整目标位置。)"
                    )
            elif arrive_mode == "p2p":
                threading.Thread(target=openapex_commander.pub_ja, args=(rst_ja,)).start()
                for i, a in enumerate(rst_ja[-1, :]):
                    c = round((a / 360.0) * 310464.0)
                    f = 0 if c >= 0 else 1
                    openapex_commander.pum.send_data(
                        Pos_Control(i + 1, f, 500, 127, abs(c), 1, 1)
                    )
                    time.sleep(0.0001)
                openapex_commander.pum.send_data(Synchronous_motion(0))
                time.sleep(0.0001)
                openapex_r.rot_xyz = er
                target_tool.rot = np.rad2deg(er)
        else:
            openapex_v.set_model_ja(openapex_r.ja)

    target_tool = TargetTool(
        parent=scene, model="sphere", scale=0.045, color=color.white, alpha=0.5
    )
    target_tool.world_position = openapex_v.link6.world_position
    target_tool.on_click = Func(target_tool_movement, "linear")

    def key_command(key):
        if key == "space":
            print("move to target.")
            target_tool_movement("linear")

        if key == "m":
            print("move to target.")
            target_tool_movement("p2p")

        if key == "home":
            print("return home")
            target_tool.world_position = Vec3(0.318, 0.158, -0.106)
            target_tool.rot = Vec3(0, 0, 180)

        if key == "-":
            print("task sequence start.")
            ts_mngr.start_task()

        if key == "=":
            print("task sequence finish.")
            ts_mngr.stop_task()

        if key == "end":
            print("移动至指定坐标位置")
            target_tool.world_position = Vec3(
                float(target_tool.inputf_x.text),
                float(target_tool.inputf_z.text),
                float(target_tool.inputf_y.text),
            )

    target_tool.key_command = key_command

    p = jcm.load_config("port")
    pum.connect_serial(p)
    pg = jcm.load_config("gport")
    gpum.connect_serial(pg, baudrate=115200)
    servo = BusServo(pc_uart=gpum.uart)
    openapex_commander = OpenApexCommander(pum=pum)

    def g_change():
        v = g_slider.value
        servo.run(1, int(v), 0)

    g_slider = Slider(
        min=400,
        max=550,
        default=550,
        step=1,
        round_to=1,
        dynamic=True,
        position=(-0.75, -0.45),
    )
    g_slider.on_value_changed = g_change

    app.run()

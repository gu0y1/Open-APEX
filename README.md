# Open-APEX: Affordable & Open Robotic Arm

**Open-APEX** (Open-Sourced Affordable Printed Extensible eXchangeable-tool Robotic Arm) solves the trilemma of **affordability**, **reproducibility**, and **extensibility**. A deterministic control stack built on accessible 3D-printing.

🌐 **Website**: [open-apex.org](https://open-apex.org)

> Engineering-level Reliability at Campus Cost

---

## The Open-APEX Vision

Robotics platforms limit research when they force a compromise between cost and capability. Open-APEX breaks this barrier. We deliver a **6-DoF arm**, strict **deterministic safety**, and an open **VLA-ready pipeline** — proving that affordability does not require sacrificing reproducibility or extensibility.

## Built for Under SGD 203

A complete 6-DOF robotic arm platform — including structure, actuation, power, safety systems, and workspace furniture — for less than the price of a single university textbook bundle.

## Key Capabilities

### 🏗️ Standardization & Reliability
- **PETG chassis** optimized for FDM — prints on common campus machines (0.4 mm nozzle, 0.2 mm layer height)
- Total printed mass: **930.41 g**, filament cost: ~**SGD 15**
- All joints use identical **42 mm stepper motors** (SGD 8 each) on a shared **RS-485 daisy-chain bus**

### 🎮 Interactive Digital Twin Control
- Drag-and-drop 3D control powered by **Ursina** engine
- Online inverse kinematics synchronization between digital twin and physical arm
- **PnP calibration** for camera-to-arm alignment
- Two execution modes: **Simul** (real-time) and **Preview-First** (safe teaching)

### 🛡️ Deterministic Safety
- **Damped Least Squares (DLS)** IK for singularity stability
- Joint clamping and distance-aware target extrapolation
- **Hardware E-Stop** with three isolated electrical domains (24V / 5V / 3.3V)

### 🔧 Modular eXchangeable-Tool System
- **Magnetic quick-release** — swap grippers, probes, and sensors without rewiring
- ESP32 Master-Slave wireless communication for tool control
- Strict dock/undock power sequencing for safety

### ⚡ Decoupled ZMQ Architecture
- **Flask** trajectory server for stateless on-demand replanning
- **ZMQ PUB/SUB** for high-speed module synchronization
- Separated visualization traffic from deterministic hardware traffic

### 🤖 Vision-Language-Action Pipeline
- Full autonomy loop from human intent to physical actuation
- VLA-ready architecture for AI-driven manipulation research

## Getting Started

### Prerequisites
- Python 3.12 with required packages (ursina, roboticstoolbox-python, flask, zmq, numpy, pyserial, spatialmath)
- USB-TTL adapter connected to the robotic arm

### Running the Control Program
```bash
python main.py
```
This launches both the Flask trajectory server and the Ursina-based 3D control UI.

### Hardware Setup
1. Mount the arm base on a rigid board (≥20mm thickness, ≥30cm × 30cm)
2. Connect 24-28V DC power supply (≥15A)
3. Connect USB-TTL module and note the COM port
4. Calibrate magnetic encoders on first power-up via the UI menu

### Controls
| Key | Action |
|-----|--------|
| Arrow Keys | Move end effector (X/Y) |
| Page Up/Down | Move end effector (Z) |
| Home | Return to home position |
| J/L/I/K/,/. | Rotate end effector |
| Drag 3D arrows | Set target position |
| Click sphere | Execute trajectory |

## Project Structure

```
├── main.py                    # Entry point — launches server + UI
├── openapexFlaskServer.py     # Flask trajectory server (IK solver)
├── openapexUI.py              # Ursina 3D control interface
├── openapexVirtual.py         # Digital twin visualization
├── openapexCommander.py       # ZMQ publisher + serial commander
├── openapexTargetTool.py      # 3D target navigation widget
├── busservo/                  # Bus servo (gripper) driver
├── zdtstepper/                # ZDT stepper motor protocol
├── tools/                     # JSON config & UART port managers
├── model/                     # 3D model files (.glb)
├── model2/                    # Alternative 3D models (.glb)
├── font/                      # UI fonts
├── audio/                     # Audio assets
├── ico/                       # Application icon
└── param/                     # Configuration files
```

## Community

Open-APEX is built in the open. Every contribution — from a one-line typo fix to a new end-effector module — helps the platform grow.

- 🐛 **[Report Issues](https://github.com/gu0y1/Open-APEX/issues)** — Search existing issues, use templates, include reproduction steps
- 🔀 **[Submit a PR](https://github.com/gu0y1/Open-APEX/pulls)** — Fork, branch from `main`, keep PRs focused
- 📋 **[Community Guidelines](https://open-apex.org#community)** — Be respectful, prioritize clarity, include BOM updates for hardware PRs

## Author

**Chen Guoyi**  
📧 guoyi@comp.nus.edu.sg  
🏫 NUS School of Computing

## License

© 2026 Open-APEX.org — All rights reserved.  
Supported by National University of Singapore (NUS).

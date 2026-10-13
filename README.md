# Bluetooth LE Rocket Telemetry System Using PIC32-BZ / WBZ451

A complete, end-to-end **wireless rocket telemetry system** built on Microchip's **WBZ451 (PIC32-BZ2)** Bluetooth Low Energy SoC. The system streams real-time pressure, temperature, and 3-axis acceleration data from a sensor node on the rocket to a PC ground station GUI over BLE or USB — no proprietary app or cloud service required.

---

## Table of Contents

- [What Is This Project?](#what-is-this-project)
- [Why You Need It](#why-you-need-it)
- [Application Use Cases](#application-use-cases)
- [Hardware Used](#hardware-used)
- [Software Stack](#software-stack)
- [Project Structure](#project-structure)
- [Launching the GUI — Step-by-Step](#launching-the-gui--step-by-step)
- [Firmware — How to Build and Flash](#firmware--how-to-build-and-flash)
- [Telemetry Protocol](#telemetry-protocol)
- [GUI Features](#gui-features)
- [Demo Mode](#demo-mode)
- [Frequently Asked Questions](#frequently-asked-questions)

---

## What Is This Project?

This project demonstrates how to use the **Microchip WBZ451 BLE SoC** as a wireless sensor hub for real-time telemetry. The WBZ451 reads two sensors over I2C:

- **MPL3115A2** — barometric pressure and temperature sensor
- **FXLS8974** — 3-axis accelerometer (±2 g, 12.5 Hz)

It encodes the readings into compact ASCII frames and transmits them continuously to a paired host using Microchip's **Transparent UART Profile (TRPS)** over BLE, or directly over a USB COM port when a USB-to-UART bridge is used.

A cross-platform **Python/tkinter desktop GUI** on the host receives the data and displays:

- Live strip charts for all 5 channels (P, T, AX, AY, AZ)
- Real-time altitude calculated from pressure and temperature using the barometric formula
- Peak altitude tracking with a "Capture Start" baseline feature
- Scrolling raw data monitor
- CSV data logging to disk

---

## Why You Need It

| Challenge | How This Project Solves It |
|---|---|
| Need wireless sensor data from a moving vehicle (rocket, drone, UAV) | BLE removes the need for wires or RF modules; WBZ451 handles the full BLE stack |
| Want to visualize live telemetry on a PC without writing a mobile app | Python GUI works on any Windows/macOS/Linux PC with Python 3 installed |
| Need to log flight data for analysis | One-click CSV logging captures every frame with timestamps |
| Want to evaluate Microchip's PIC32-BZ / WBZ451 for a sensor product | This is a fully working reference design with MPLAB Harmony 3 firmware |
| Want a demo you can run without hardware | Built-in Demo Mode simulates a complete rocket flight profile (boost → coast → apogee → descent) |

---

## Application Use Cases

This project — or the same architecture — applies to a wide range of real-world scenarios:

### Rocketry and High-Power Rocketry (HPR)
Monitor altitude, peak G-force, and flight phase (boost, coast, apogee, recovery) wirelessly. Log data for post-flight analysis and certification.

### Drone and UAV Telemetry
Stream IMU (accelerometer) and barometric altitude data from a drone to a ground station in real time over BLE.

### Weather Balloon and High-Altitude Balloon (HAB) Payloads
Log pressure, temperature, and altitude throughout a balloon flight. Capture peak altitude and rate of ascent/descent.

### Educational STEM Projects
Teach students about embedded systems, BLE communication, sensor integration, barometric altitude, and data visualization — with a working hardware+software demo.

### IoT Sensor Node Prototyping
Use the WBZ451 as a rapid prototyping platform for any I2C sensor. The Transparent UART Profile acts as a generic serial-over-BLE channel, so you can replace the sensors without changing the BLE stack.

### Wearable and Sports Performance Monitoring
Adapt the accelerometer data pipeline for impact detection, vibration analysis, or motion logging in sports equipment.

### Industrial Vibration and Condition Monitoring
Mount the sensor node on machinery. Stream accelerometer data to the PC GUI to detect abnormal vibration signatures.

### Consumer Electronics Reference Design
Demonstrates Microchip's full BLE SDK, FreeRTOS integration, MPLAB Harmony 3 middleware, and sensor driver patterns — ready to adapt for a product.

---

## Hardware Used

| Component | Part Number | Role |
|---|---|---|
| BLE SoC / MCU | **Microchip WBZ451** (PIC32-BZ2 family) | Runs firmware, BLE stack, reads sensors |
| Pressure + Temperature Sensor | **NXP MPL3115A2** | Barometric pressure (Pa) and temperature (°C) via I2C |
| 3-Axis Accelerometer | **NXP FXLS8974** | Acceleration X/Y/Z (±2 g, 12.5 Hz ODR) via I2C |
| I2C Bus | SERCOM2 on WBZ451 | Connects both sensors to the MCU |
| PC / Laptop | Any Windows / macOS / Linux machine | Runs the Python ground station GUI |
| BLE transport | Integrated in WBZ451 | Wireless link to PC host adapter |
| USB-UART bridge (optional) | Any CP2102 / CH340 adapter | Wired COM port alternative to BLE |

> **Sensor interface:** Both sensors are connected to the WBZ451 via a shared I2C bus (SERCOM2). The firmware auto-detects both sensors at startup using WHO_AM_I register verification.

---

## Software Stack

### Firmware (WBZ451)

| Component | Details |
|---|---|
| IDE | MPLAB X IDE |
| Framework | MPLAB Harmony 3 |
| RTOS | FreeRTOS |
| BLE Stack | Microchip BLE SDK (PIC32-BZ2) |
| BLE Profile | Transparent UART Profile Server (TRPS) |
| Language | C |
| Project file | `Rocket_Telemetry/Rocket_Telemetry.X/` |

### Ground Station GUI

| Component | Details |
|---|---|
| Language | Python 3.9+ |
| GUI Framework | tkinter (built into Python) |
| Charts | matplotlib (embedded via FigureCanvasTkAgg) |
| BLE | bleak (cross-platform BLE library) |
| Serial | pyserial |
| Packaging | PyInstaller (`.spec` file included) |

---

## Project Structure

```
Bluetooth-LE-Rocket-Telemetry-System-Using-PIC32-BZ-MCUs/
│
├── Rocket_Telemetry/                    # WBZ451 firmware (MPLAB X project)
│   ├── Rocket_Telemetry.X/              # MPLAB X project files
│   └── src/
│       ├── app.c / app.h                # Sensor init, read, and main state machine
│       ├── app_ble/                     # BLE event handlers and TRPS handler
│       ├── app_trps.c / app_trps.h      # Transparent UART Profile server logic
│       └── config/default/              # Harmony 3 generated config (BLE stack, FreeRTOS)
│
└── Rocket_Telemetry_GUI/                # Python ground station GUI
    ├── app.py                           # Main application (all GUI + BLE + serial logic)
    ├── requirements.txt                 # Python dependencies (bleak, pyserial)
    ├── app.spec                         # PyInstaller build spec for .exe packaging
    ├── Microchip_logo.png               # Logo displayed in the GUI footer
    └── rocket.ico / rocket.png          # App icons
```

---

## Launching the GUI — Step-by-Step

### Prerequisites

- Python 3.9 or later ([python.org](https://www.python.org/downloads/))
- The GUI folder at your chosen path (e.g., `d:\RocketGUI 2\RocketGUI`)

### Step 1 — Open a Terminal (Command Prompt or PowerShell)

On Windows, press `Win + R`, type `cmd`, press Enter.

### Step 2 — Navigate to the GUI Folder

```bat
cd "d:\RocketGUI 2\RocketGUI"
```

### Step 3 — Install Python Dependencies

```bat
pip install -r requirements.txt
pip install matplotlib
```

> These commands install **bleak** (BLE), **pyserial** (COM port), and **matplotlib** (charts).  
> You only need to run this once. If you see "already satisfied", that is fine.

### Step 4 — Run the GUI

```bat
python app.py
```

The **Port and BLE Connector** main window opens. You are ready to connect.

### Step 5 — Connect to the WBZ451

**Over BLE:**
1. Select **Bluetooth BLE** in the Transport section.
2. Click **Scan BLE** — wait a few seconds for devices to appear.
3. Select your WBZ451 device in the list (e.g., `BLE_UART_DEMO` or a custom name).
4. Click **Connect**.

**Over USB COM Port:**
1. Plug the USB-UART adapter into your PC.
2. Select **COM Port** in the Transport section.
3. Click **Scan COM** — your port appears in the list (e.g., `COM15`).
4. Set Baud to `115200`.
5. Select the port and click **Connect**.

### Step 6 — Open Telemetry Windows

After connecting, use the **Windows** row of buttons:

- **Raw On/Off** — scrolling view of raw telemetry frames
- **Chart On/Off** — 5-channel strip chart (P, T, AX, AY, AZ)
- **Altitude On/Off** — altitude strip chart with peak and baseline capture

### Step 7 — (Optional) Log Data to CSV

Click **Start Log** to begin recording all telemetry frames to a timestamped `.csv` file in the same folder as `app.py`. Click **Stop Log** to close the file.

---

## Firmware — How to Build and Flash

1. Install **MPLAB X IDE** and the **XC32 compiler** from [microchip.com/mplab](https://www.microchip.com/en-us/tools-resources/develop/mplab-x-ide).
2. Open `Rocket_Telemetry/Rocket_Telemetry.X/` as an existing project in MPLAB X.
3. Select the **WBZ451** as the target device.
4. Build the project (F11).
5. Connect your WBZ451 development board via the PKOB (MPLAB PICkit On Board) or an external programmer.
6. Program the device (F6 / Make and Program Device).

After programming, the WBZ451 will advertise as a BLE peripheral and begin streaming sensor data as soon as both the MPL3115A2 and FXLS8974 are detected on the I2C bus.

> The firmware can also forward data via UART at 115200 baud on the SERCOM-mapped TX/RX pins, which lets a USB-UART adapter substitute for BLE during development.

---

## Telemetry Protocol

The WBZ451 sends data as **framed ASCII over BLE Transparent UART (or UART)**:

```
<P,T,AX,AY,AZ\n\r>
```

| Field | Unit | Example |
|---|---|---|
| `P` | kPa | `101.325` |
| `T` | °C | `24.500` |
| `AX` | g | `0.012` |
| `AY` | g | `-0.005` |
| `AZ` | g | `1.001` |

Frame delimiter: `<` start, `\n\r` end. The GUI extracts complete frames from the raw byte stream and discards partial frames automatically.

**Altitude calculation** (hypsometric formula):

```
altitude_m = (R × T_K / g) × ln(P0 / P)
```

Where R = 287.05 J/(kg·K), g = 9.80665 m/s², P0 = 101325 Pa.

---

## GUI Features

| Feature | Description |
|---|---|
| BLE scan and connect | Discovers all nearby BLE peripherals; connects to any TRPS-compatible device |
| COM port scan and connect | Auto-discovers COM ports; supports any baud rate |
| Strip chart — 5 channels | Real-time scrolling plots for P, T, AX, AY, AZ; configurable Y-axis min/max; Auto Range button |
| Altitude chart | Barometric altitude in metres; peak altitude tracking; "Capture Start" zeros the baseline |
| Raw data monitor | Scrolling text view of decoded frames; Clear button |
| CSV logging | Timestamped log files: `Timestamp, P_kPa, T_degC, AX_g, AY_g, AZ_g, Altitude_m` |
| Demo mode | Simulated rocket flight (no hardware needed); plays back a generated 20-second flight CSV |
| Disconnect | Cleanly disconnects BLE or COM, closes sub-windows, stops logging |

---

## Demo Mode

Click **Demo Start** to run a simulated rocket flight with no hardware attached. The demo:

1. Generates a flight CSV internally (boost → coast → apogee at ~327 m / ~1073 ft → descent).
2. Opens the Raw Data Monitor, Strip Chart, and Altitude windows automatically.
3. Plays back one data point every 100 ms (10 Hz) over 20 seconds.
4. Stops automatically when the flight profile ends.

This is useful for:
- Evaluating the GUI before hardware is available
- Training new users on what real flight data looks like
- Trade show and classroom demonstrations

---

## Frequently Asked Questions

**Q: Can I use a different BLE chip instead of WBZ451?**  
A: The GUI is hardware-agnostic. Any BLE device that implements the Transparent UART Profile (TRPS) and sends the `<P,T,AX,AY,AZ\n\r>` frame format will work. You can also replace BLE with a plain COM port if you have a UART connection.

**Q: What Python version is required?**  
A: Python 3.9 or later. Type `python --version` in a terminal to check.

**Q: Can I build a standalone .exe so users don't need Python?**  
A: Yes. A PyInstaller spec file (`app.spec`) is included. Run `pyinstaller app.spec` in the GUI folder to produce a single-file Windows executable.

**Q: Can I change the sensors?**  
A: Yes. Edit `app.c` in the firmware to read different I2C sensors and format them into the same ASCII frame. No changes to the GUI are needed as long as the frame format stays the same.

**Q: What is the maximum BLE range?**  
A: The WBZ451 supports Bluetooth 5.2. In open-air conditions, range typically exceeds 50 m at 2M PHY and can reach hundreds of metres at Coded PHY (S8), depending on antenna and environment.

**Q: Can I log multiple flights in one session?**  
A: Yes. Each click of **Start Log** creates a new timestamped CSV file. Old log files are not overwritten.

---

## Related Topics and Keywords

Microchip WBZ451 · PIC32-BZ2 · BLE SoC · Transparent UART Profile · TRPS · MPLAB Harmony 3 · FreeRTOS · MPL3115A2 · FXLS8974 · barometric altitude · rocket telemetry · high-power rocketry data logger · Bluetooth Low Energy sensor streaming · BLE to PC GUI · Python BLE · bleak · real-time sensor visualization · IMU data logging · IoT sensor node · wireless data acquisition · embedded BLE firmware · MPLAB X · XC32 · altitude from pressure · hypsometric formula · amateur rocketry · model rocket flight computer · drone telemetry · UAV sensor · accelerometer BLE · pressure sensor BLE · Microchip PIC32 BLE demo

---

*Copyright (C) 2022–2024 Microchip Technology Inc. and its subsidiaries. Firmware source files are subject to Microchip's standard software license agreement. See source file headers for full license text.*

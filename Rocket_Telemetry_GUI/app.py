import asyncio
import concurrent.futures
import csv
import datetime
import math
import os
import threading
import tkinter as tk
from collections import deque
from dataclasses import dataclass
from tkinter import messagebox, ttk
from typing import Callable

_LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "microchip_logo.png")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from bleak import BleakClient, BleakScanner
import serial
from serial.tools import list_ports

_FRAME_START = "<"
_FRAME_END = "\n\r"
_SENSOR_KEYS = ["P", "T", "AX", "AY", "AZ"]
_SEA_LEVEL_PRESSURE_PA = 101325.0
_GRAVITY_MPS2 = 9.80665
_DRY_AIR_SPECIFIC_GAS_CONSTANT = 287.05

_CHART_CHANNELS: list[tuple[str, str, str, str]] = [
    ("P",  "Pressure",    "kPa", "#00008B"),
    ("T",  "Temperature", "\u00b0C",  "#00008B"),
    ("AX", "Accel X",     "g",   "#00008B"),
    ("AY", "Accel Y",     "g",   "#00008B"),
    ("AZ", "Accel Z",     "g",   "#00008B"),
]
_MAX_SAMPLES = 200

# (min_options, default_min, max_options, default_max) per channel
_CHANNEL_RANGE_OPTIONS: dict[str, tuple[list[str], str, list[str], str]] = {
    "P":  ([str(v) for v in range(50, 101, 5)],   "70",  [str(v) for v in range(75, 131, 5)],  "105"),
    "T":  ([str(v) for v in range(-50, 26, 5)],   "-5",  [str(v) for v in range(0, 81, 5)],    "50"),
    "AX": ([str(v) for v in range(-32, 1, 2)],    "-16", [str(v) for v in range(2, 34, 2)],    "16"),
    "AY": ([str(v) for v in range(-32, 1, 2)],    "-16", [str(v) for v in range(2, 34, 2)],    "16"),
    "AZ": ([str(v) for v in range(-32, 1, 2)],    "-16", [str(v) for v in range(2, 34, 2)],    "16"),
}


@dataclass
class DeviceEntry:
    kind: str
    label: str
    identifier: str
    details: str = ""


class BleWorker:
    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._client: BleakClient | None = None
        self._notify_characteristics: list[str] = []

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro: asyncio.coroutines) -> asyncio.Future:
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    async def scan(self, timeout: float = 5.0) -> list[DeviceEntry]:
        devices = await BleakScanner.discover(timeout=timeout, return_adv=True)
        entries: list[DeviceEntry] = []

        for address, pair in devices.items():
            device, adv = pair
            name = device.name or adv.local_name or "Unknown BLE Device"
            rssi = adv.rssi
            details = f"RSSI {rssi} dBm" if rssi is not None else ""
            entries.append(
                DeviceEntry(
                    kind="BLE",
                    label=name,
                    identifier=address,
                    details=details,
                )
            )

        entries.sort(key=lambda entry: entry.label.lower())
        return entries

    async def connect(
        self,
        address: str,
        on_data: Callable[[bytes], None],
    ) -> int:
        await self.disconnect()
        client = BleakClient(address)
        await client.connect()
        self._client = client
        self._notify_characteristics = []

        for service in client.services:
            for characteristic in service.characteristics:
                if "notify" not in characteristic.properties and "indicate" not in characteristic.properties:
                    continue

                await client.start_notify(characteristic.uuid, self._build_notification_handler(on_data))
                self._notify_characteristics.append(characteristic.uuid)

        return len(self._notify_characteristics)

    def _build_notification_handler(
        self,
        on_data: Callable[[bytes], None],
    ) -> Callable[[object, bytearray], None]:
        def handle_notification(_: object, data: bytearray) -> None:
            on_data(bytes(data))

        return handle_notification

    async def disconnect(self) -> bool:
        if self._client is not None:
            for uuid in self._notify_characteristics:
                await self._client.stop_notify(uuid)
            self._notify_characteristics.clear()
            await self._client.disconnect()
            self._client = None
            return True

        return False


class StripChartWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self._parent = parent
        self.window: tk.Toplevel | None = None
        self._buffers: dict[str, deque[float]] = {
            key: deque(maxlen=_MAX_SAMPLES) for key, *_ in _CHART_CHANNELS
        }
        self._dirty = False
        self._fig: plt.Figure | None = None
        self._axes: list = []
        self._lines: list = []
        self._value_texts: list = []
        self._canvas: FigureCanvasTkAgg | None = None
        self._after_id: str | None = None
        self._axis_mins: dict[str, tk.StringVar] = {
            key: tk.StringVar(value=opts[1])
            for key, opts in _CHANNEL_RANGE_OPTIONS.items()
        }
        self._axis_maxs: dict[str, tk.StringVar] = {
            key: tk.StringVar(value=opts[3])
            for key, opts in _CHANNEL_RANGE_OPTIONS.items()
        }

    def open(self, title: str) -> None:
        if self.window is not None and self.window.winfo_exists():
            self.window.title(title)
            self.window.deiconify()
            self.window.lift()
            return

        self.window = tk.Toplevel(self._parent)
        self.window.title(title)
        self.window.geometry("1120x720")
        self.window.configure(bg="#1a1a1a")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=0)
        self.window.rowconfigure(0, weight=1)

        self._fig, axes = plt.subplots(
            len(_CHART_CHANNELS), 1,
            figsize=(9.2, 7.2),
            facecolor="white",
        )
        self._axes = list(axes)
        self._fig.subplots_adjust(hspace=0.65, left=0.14, right=0.97, top=0.97, bottom=0.04)
        self._lines = []
        self._value_texts = []

        for ax, (key, label, unit, color) in zip(self._axes, _CHART_CHANNELS):
            ax.set_facecolor("white")
            (line,) = ax.plot([], [], color=color, linewidth=1.3, antialiased=True)
            self._lines.append(line)
            value_text = ax.text(
                0.5,
                1.02,
                f"Current: -- {unit}",
                transform=ax.transAxes,
                ha="center",
                va="bottom",
                color="black",
                fontsize=8,
            )
            self._value_texts.append(value_text)
            ax.set_ylabel(f"{label}\n({unit})", color="black", fontsize=7.5, labelpad=6)
            ax.tick_params(axis="both", colors="black", labelsize=7)
            ax.grid(axis="y", color="#cccccc", linewidth=0.8, linestyle="--")
            ax.grid(axis="x", color="#dddddd", linewidth=0.5)
            for spine in ax.spines.values():
                spine.set_edgecolor("black")
            ax.set_xlim(0, _MAX_SAMPLES)
            ax.set_ylim(-1, 1)

        self._canvas = FigureCanvasTkAgg(self._fig, master=self.window)
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self._canvas.draw()

        controls = ttk.Frame(self.window, padding=(8, 12, 8, 8))
        controls.grid(row=0, column=1, sticky="ns")
        ttk.Label(controls, text="Axis Ranges", font=("TkDefaultFont", 9, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 10)
        )
        for row_idx, (key, label, unit, _) in enumerate(_CHART_CHANNELS, start=1):
            opts = _CHANNEL_RANGE_OPTIONS[key]
            ttk.Label(controls, text=f"{label}", width=11).grid(
                row=row_idx, column=0, sticky="w", pady=6
            )
            ttk.Label(controls, text="Min:").grid(row=row_idx, column=1, sticky="e", padx=(6, 2))
            ttk.Combobox(
                controls,
                textvariable=self._axis_mins[key],
                values=opts[0],
                width=5,
                state="readonly",
            ).grid(row=row_idx, column=2, sticky="w")
            ttk.Label(controls, text="Max:").grid(row=row_idx, column=3, sticky="e", padx=(6, 2))
            ttk.Combobox(
                controls,
                textvariable=self._axis_maxs[key],
                values=opts[2],
                width=5,
                state="readonly",
            ).grid(row=row_idx, column=4, sticky="w")

        ttk.Button(controls, text="Apply Ranges", command=self.apply_ranges).grid(
            row=len(_CHART_CHANNELS) + 1, column=0, columnspan=5, sticky="ew", pady=(12, 0)
        )
        ttk.Button(controls, text="Auto Range", command=self.auto_range).grid(
            row=len(_CHART_CHANNELS) + 2, column=0, columnspan=5, sticky="ew", pady=(6, 0)
        )

        self._schedule_redraw()

    def push(self, values: dict[str, float]) -> None:
        for key, value in values.items():
            if key in self._buffers:
                self._buffers[key].append(value)
        self._dirty = True

    def reset(self) -> None:
        for buf in self._buffers.values():
            buf.clear()
        self._dirty = True

    def apply_ranges(self) -> None:
        if self.window is None or not self.window.winfo_exists():
            return
        self._dirty = True
        self._redraw()
        self._dirty = False

    def auto_range(self) -> None:
        any_data = False
        for key, *_ in _CHART_CHANNELS:
            data = list(self._buffers[key])
            if not data:
                continue

            any_data = True
            data_min = min(data)
            data_max = max(data)
            span = data_max - data_min
            margin_ratio = 0.25 if key == "P" else 0.05
            if span > 0:
                margin = span * margin_ratio
            else:
                margin = max(1.0, abs(data_max) * margin_ratio)

            self._axis_mins[key].set(f"{data_min - margin:.2f}")
            self._axis_maxs[key].set(f"{data_max + margin:.2f}")

        if not any_data:
            messagebox.showinfo("Auto Range", "No chart data available for auto range yet.")
            return

        self.apply_ranges()

    def _schedule_redraw(self) -> None:
        if self.window is None or not self.window.winfo_exists():
            return
        if self._dirty:
            self._redraw()
            self._dirty = False
        self._after_id = self.window.after(100, self._schedule_redraw)

    def _redraw(self) -> None:
        for line, value_text, (key, _, unit, _) in zip(self._lines, self._value_texts, _CHART_CHANNELS):
            data = list(self._buffers[key])
            n = len(data)
            if n == 0:
                continue
            line.set_data(range(n), data)
            value_text.set_text(f"Current: {data[-1]:.2f} {unit}")
            ax = line.axes
            try:
                ymin = float(self._axis_mins[key].get())
                ymax = float(self._axis_maxs[key].get())
            except (KeyError, ValueError):
                ymin, ymax = -1.0, 1.0
            ax.set_ylim(ymin, ymax)
        self._canvas.draw_idle()

    def close(self) -> None:
        if self._after_id is not None and self.window is not None:
            try:
                self.window.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = None
        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None
        if self.window is not None and self.window.winfo_exists():
            self.window.destroy()
        self.window = None
        self._axes = []
        self._lines = []
        self._value_texts = []
        self._canvas = None


class AltitudeWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self._parent = parent
        self.window: tk.Toplevel | None = None
        self._buffer: deque[float] = deque(maxlen=_MAX_SAMPLES)
        self._dirty = False
        self._fig: plt.Figure | None = None
        self._ax = None
        self._line = None
        self._value_text = None
        self._canvas: FigureCanvasTkAgg | None = None
        self._after_id: str | None = None
        self._peak_altitude_m = float("-inf")
        self._peak_var = tk.StringVar(value="Peak: -- m")
        self._start_altitude_var = tk.StringVar(value="Start: -- m")
        self._max_range_var = tk.StringVar(value="2000")
        self._min_range_var = tk.StringVar(value="-10")
        self._latest_raw_altitude_m: float | None = None
        self._altitude_offset_m: float | None = None

    def open(self, title: str) -> None:
        if self.window is not None and self.window.winfo_exists():
            self.window.title(title)
            self.window.deiconify()
            self.window.lift()
            return

        self.window = tk.Toplevel(self._parent)
        self.window.title(title)
        self.window.geometry("900x420")
        self.window.configure(bg="#1a1a1a")
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        container = ttk.Frame(self.window, padding=8)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        top_bar = ttk.Frame(container)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.columnconfigure(0, weight=1)
        ttk.Label(top_bar, text="Altitude (calculated from P and T)").grid(row=0, column=0, sticky="w")
        ttk.Label(top_bar, textvariable=self._peak_var).grid(row=0, column=1, sticky="e", padx=(12, 12))
        ttk.Label(top_bar, textvariable=self._start_altitude_var).grid(row=0, column=2, sticky="e", padx=(0, 12))
        ttk.Button(top_bar, text="Capture Start", command=self.capture_starting_altitude).grid(
            row=0, column=3, sticky="e", padx=(0, 12)
        )
        ttk.Label(top_bar, text="Max (m):").grid(row=0, column=4, sticky="e")
        range_values = [str(v) for v in range(50, 3050, 50)]
        range_box = ttk.Combobox(
            top_bar,
            textvariable=self._max_range_var,
            values=range_values,
            width=6,
            state="readonly",
        )
        range_box.grid(row=0, column=5, sticky="e", padx=(4, 0))
        ttk.Label(top_bar, text="Min (m):").grid(row=0, column=6, sticky="e", padx=(12, 0))
        min_values = [str(v) for v in range(-100, 550, 50)]
        min_box = ttk.Combobox(
            top_bar,
            textvariable=self._min_range_var,
            values=min_values,
            width=6,
            state="readonly",
        )
        min_box.grid(row=0, column=7, sticky="e", padx=(4, 0))
        ttk.Button(top_bar, text="Apply Range", command=self.apply_range).grid(
            row=0, column=8, sticky="e", padx=(12, 0)
        )
        ttk.Button(top_bar, text="Auto Range", command=self.auto_range).grid(
            row=0, column=9, sticky="e", padx=(8, 0)
        )

        self._fig, self._ax = plt.subplots(1, 1, figsize=(8.8, 3.7), facecolor="white")
        self._ax.set_facecolor("white")
        (self._line,) = self._ax.plot([], [], color="#4dd0e1", linewidth=1.5, antialiased=True)
        self._value_text = self._ax.text(
            0.5,
            1.02,
            "Current: -- m",
            transform=self._ax.transAxes,
            ha="center",
            va="bottom",
            color="black",
            fontsize=9,
        )
        self._ax.set_ylabel("Altitude\n(m)", color="black", fontsize=8, labelpad=8)
        self._ax.tick_params(axis="both", colors="black", labelsize=8)
        self._ax.grid(axis="y", color="#cccccc", linewidth=0.8, linestyle="--")
        self._ax.grid(axis="x", color="#dddddd", linewidth=0.5)
        for spine in self._ax.spines.values():
            spine.set_edgecolor("black")
        self._ax.set_xlim(0, _MAX_SAMPLES)
        self._ax.set_ylim(-10, 2000)

        self._canvas = FigureCanvasTkAgg(self._fig, master=container)
        self._canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self._canvas.draw()
        self._schedule_redraw()

    def push(self, altitude_m: float) -> None:
        self._latest_raw_altitude_m = altitude_m
        adjusted_altitude_m = self.adjust_altitude(altitude_m)

        self._buffer.append(adjusted_altitude_m)
        if adjusted_altitude_m > self._peak_altitude_m:
            self._peak_altitude_m = adjusted_altitude_m
            self._peak_var.set(f"Peak: {adjusted_altitude_m:.2f} m")
        self._dirty = True

    def adjust_altitude(self, altitude_m: float) -> float:
        if self._altitude_offset_m is None:
            return altitude_m
        return altitude_m - self._altitude_offset_m

    def capture_starting_altitude(self) -> None:
        if self._latest_raw_altitude_m is None:
            messagebox.showinfo("No Altitude Yet", "Wait for altitude data, then capture start altitude.")
            return

        self._altitude_offset_m = self._latest_raw_altitude_m
        self._start_altitude_var.set(f"Start: {self._altitude_offset_m:.2f} m")

        # Reset the chart so the baseline-captured altitude starts from zero.
        self._buffer.clear()
        self._buffer.append(0.0)
        self._peak_altitude_m = 0.0
        self._peak_var.set("Peak: 0.00 m")
        self._dirty = True

    def reset(self) -> None:
        self._buffer.clear()
        self._peak_altitude_m = float("-inf")
        self._peak_var.set("Peak: -- m")
        self._start_altitude_var.set("Start: -- m")
        self._latest_raw_altitude_m = None
        self._altitude_offset_m = None
        self._dirty = True

    def apply_range(self) -> None:
        if self.window is None or not self.window.winfo_exists():
            return
        self._dirty = True
        self._redraw()
        self._dirty = False

    def auto_range(self) -> None:
        data = list(self._buffer)
        if not data:
            messagebox.showinfo("Auto Range", "No altitude data available for auto range yet.")
            return

        data_min = min(data)
        data_max = max(data)
        span = data_max - data_min
        if span > 0:
            margin = span * 0.05
        else:
            margin = max(1.0, abs(data_max) * 0.05)

        self._min_range_var.set(f"{data_min - margin:.2f}")
        self._max_range_var.set(f"{data_max + margin:.2f}")
        self.apply_range()

    def _schedule_redraw(self) -> None:
        if self.window is None or not self.window.winfo_exists():
            return
        if self._dirty:
            self._redraw()
            self._dirty = False
        self._after_id = self.window.after(100, self._schedule_redraw)

    def _redraw(self) -> None:
        if self._line is None:
            return
        data = list(self._buffer)
        n = len(data)
        if n == 0:
            if self._canvas is not None:
                self._canvas.draw_idle()
            return

        self._line.set_data(range(n), data)
        if self._value_text is not None:
            self._value_text.set_text(f"Current: {data[-1]:.2f} m")
        ax = self._line.axes
        try:
            max_val = float(self._max_range_var.get())
        except ValueError:
            max_val = 2000.0
        try:
            min_val = float(self._min_range_var.get())
        except ValueError:
            min_val = -10.0
        if min_val >= max_val:
            min_val, max_val = -10.0, 2000.0
        ax.set_ylim(min_val, max_val)
        if self._canvas is not None:
            self._canvas.draw_idle()

    def close(self) -> None:
        if self._after_id is not None and self.window is not None:
            try:
                self.window.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = None
        if self._fig is not None:
            plt.close(self._fig)
            self._fig = None
        if self.window is not None and self.window.winfo_exists():
            self.window.destroy()
        self.window = None
        self._ax = None
        self._line = None
        self._value_text = None
        self._canvas = None


class DataWindow:
    def __init__(self, parent: tk.Tk, on_close: Callable[[], None]) -> None:
        self._parent = parent
        self._on_close = on_close
        self.window: tk.Toplevel | None = None
        self.text: tk.Text | None = None

    def open(self, title: str) -> None:
        if self.window is None or not self.window.winfo_exists():
            self.window = tk.Toplevel(self._parent)
            self.window.geometry("780x420")
            self.window.protocol("WM_DELETE_WINDOW", self._handle_close)

            frame = ttk.Frame(self.window, padding=12)
            frame.grid(row=0, column=0, sticky="nsew")
            self.window.columnconfigure(0, weight=1)
            self.window.rowconfigure(0, weight=1)
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)

            self.text = tk.Text(frame, wrap="none", height=20)
            self.text.grid(row=0, column=0, sticky="nsew")

            y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.text.yview)
            y_scroll.grid(row=0, column=1, sticky="ns")
            self.text.configure(yscrollcommand=y_scroll.set)

            clear_button = ttk.Button(frame, text="Clear", command=self.clear)
            clear_button.grid(row=1, column=0, sticky="w", pady=(10, 0))

        self.window.title(title)
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()

    def append(self, line: str) -> None:
        if self.text is None or not self.window or not self.window.winfo_exists():
            return
        self.text.insert(tk.END, line + "\n")
        self.text.see(tk.END)

    def clear(self) -> None:
        if self.text is None:
            return
        self.text.delete("1.0", tk.END)

    def close(self) -> None:
        if self.window is not None and self.window.winfo_exists():
            self.window.destroy()
        self.window = None
        self.text = None

    def _handle_close(self) -> None:
        self.close()
        self._on_close()


class ConnectionApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Port and BLE Connector")
        self.root.geometry("760x480")

        self.ble_worker = BleWorker()
        self.serial_connection: serial.Serial | None = None
        self.serial_reader_thread: threading.Thread | None = None
        self.serial_reader_stop = threading.Event()
        self.device_entries: list[DeviceEntry] = []
        self.com_entries: list[DeviceEntry] = []
        self.ble_entries: list[DeviceEntry] = []
        self.com_scan_thread: threading.Thread | None = None
        self.com_scan_stop = threading.Event()
        self.com_scanning = False
        self.ble_scan_future: asyncio.Future | None = None
        self.ble_scan_stop = threading.Event()
        self.ble_scanning = False
        self.data_window = DataWindow(root, self.disconnect_current)
        self.strip_chart = StripChartWindow(root)
        self.altitude_window = AltitudeWindow(root)
        self.pending_display_data: dict[str, str] = {}
        self.raw_window_title = "Raw Data Monitor"
        self.strip_chart_title = "Strip Chart"
        self.altitude_window_title = "Altitude"

        self._csv_file: object = None
        self._csv_writer: csv.writer | None = None
        self._log_index: int = 0
        self._log_lock = threading.Lock()
        self._demo_running = False
        self._demo_after_id: str | None = None
        self._demo_end_time = 0.0
        self._demo_tick = 0
        self._demo_file_index: int = 0
        self._demo_reader_file: object = None
        self._demo_reader: csv.DictReader | None = None
        self._demo_total_rows = 200
        self._demo_rows_played = 0

        self.transport_var = tk.StringVar(value="COM")
        self.status_var = tk.StringVar(value="Ready")
        self.baud_rate_var = tk.StringVar(value="115200")
        self.connected_label_var = tk.StringVar(value="Not connected")

        self._build_ui()
        self.scan_com_ports()
        self.root.protocol("WM_DELETE_WINDOW", self._on_app_close)

    def _on_app_close(self) -> None:
        self._stop_demo()
        self._stop_logging(silent=True)
        self.root.destroy()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)
        self.root.rowconfigure(0, weight=1)

        list_frame = ttk.Frame(self.root, padding=(12, 12, 6, 12))
        list_frame.grid(row=0, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)

        ttk.Label(list_frame, text="Discovered devices and ports").grid(
            row=0, column=0, sticky="w"
        )

        self.device_list = tk.Listbox(list_frame, height=16)
        self.device_list.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.device_list.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(8, 0))
        self.device_list.configure(yscrollcommand=scrollbar.set)

        controls = ttk.Frame(self.root, padding=(6, 12, 12, 12))
        controls.grid(row=0, column=1, sticky="ns")
        controls.columnconfigure(0, weight=1)

        ttk.Label(controls, text="Transport").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(
            controls,
            text="COM Port",
            value="COM",
            variable=self.transport_var,
            command=self._refresh_transport_ui,
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Radiobutton(
            controls,
            text="Bluetooth BLE",
            value="BLE",
            variable=self.transport_var,
            command=self._refresh_transport_ui,
        ).grid(row=2, column=0, sticky="w")

        self.baud_label = ttk.Label(controls, text="Baud")
        self.baud_label.grid(row=3, column=0, sticky="w", pady=(12, 0))
        self.baud_entry = ttk.Entry(controls, textvariable=self.baud_rate_var, width=12)
        self.baud_entry.grid(
            row=4, column=0, sticky="ew", pady=(4, 12)
        )

        self.scan_com_button = ttk.Button(controls, text="Scan COM", command=self.toggle_com_scan)
        self.scan_com_button.grid(
            row=5, column=0, sticky="ew", pady=(0, 6)
        )
        self.scan_ble_button = ttk.Button(controls, text="Scan BLE", command=self.toggle_ble_scan)
        self.scan_ble_button.grid(
            row=6, column=0, sticky="ew", pady=(0, 6)
        )
        self.connect_button = ttk.Button(controls, text="Connect", command=self._toggle_connection)
        self.connect_button.grid(
            row=7, column=0, sticky="ew", pady=(0, 6)
        )

        ttk.Separator(controls, orient="horizontal").grid(row=9, column=0, sticky="ew", pady=(12, 8))
        ttk.Label(controls, text="Windows").grid(row=10, column=0, sticky="w")

        window_buttons = ttk.Frame(controls)
        window_buttons.grid(row=11, column=0, sticky="ew", pady=(6, 0))
        window_buttons.columnconfigure(0, weight=1)
        window_buttons.columnconfigure(1, weight=1)
        window_buttons.columnconfigure(2, weight=1)

        ttk.Button(window_buttons, text="Raw On/Off", command=self._toggle_raw_window).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(window_buttons, text="Chart On/Off", command=self._toggle_strip_chart_window).grid(
            row=0, column=1, sticky="ew", padx=4
        )
        ttk.Button(window_buttons, text="Altitude On/Off", command=self._toggle_altitude_window).grid(
            row=0, column=2, sticky="ew", padx=(4, 0)
        )

        ttk.Separator(controls, orient="horizontal").grid(row=12, column=0, sticky="ew", pady=(12, 8))
        ttk.Label(controls, text="CSV Logging", font=("TkDefaultFont", 9, "bold")).grid(
            row=13, column=0, sticky="w"
        )
        log_buttons = ttk.Frame(controls)
        log_buttons.grid(row=14, column=0, sticky="ew", pady=(6, 0))
        log_buttons.columnconfigure(0, weight=1)
        log_buttons.columnconfigure(1, weight=1)
        ttk.Button(log_buttons, text="Start Log", command=self._start_logging).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(log_buttons, text="Stop Log", command=self._stop_logging).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

        ttk.Separator(controls, orient="horizontal").grid(row=15, column=0, sticky="ew", pady=(12, 8))
        self.demo_button = ttk.Button(controls, text="Demo Start", command=self._toggle_demo)
        self.demo_button.grid(row=16, column=0, sticky="ew")

        footer = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        footer.grid(row=1, column=0, columnspan=2, sticky="ew")
        footer.columnconfigure(1, weight=1)
        footer.columnconfigure(2, weight=0)

        ttk.Label(footer, text="Selected connection").grid(row=0, column=0, sticky="w")
        ttk.Label(footer, textvariable=self.connected_label_var).grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )
        ttk.Label(footer, textvariable=self.status_var).grid(row=1, column=0, columnspan=2, sticky="w")

        self._logo_image: tk.PhotoImage | None = None
        self._load_logo(footer)

        self._refresh_transport_ui()
        self._update_connection_button_label()

    def _load_logo(self, footer: ttk.Frame) -> None:
        if not os.path.exists(_LOGO_PATH):
            return
        try:
            from PIL import Image, ImageTk
            pil_img = Image.open(_LOGO_PATH)
            target_h = 48
            ratio = target_h / pil_img.height
            pil_img = pil_img.resize(
                (int(pil_img.width * ratio), target_h),
                Image.LANCZOS,
            )
            self._logo_image = ImageTk.PhotoImage(pil_img)
            logo_label = ttk.Label(footer, image=self._logo_image)
            logo_label.grid(row=0, column=2, rowspan=2, sticky="se", padx=(16, 0))
        except Exception:
            pass

    def _refresh_selection_hint(self) -> None:
        mode = self.transport_var.get()
        self.status_var.set(f"Ready to connect using {mode}")

    def _refresh_transport_ui(self) -> None:
        mode = self.transport_var.get()
        self._update_scan_button_labels()
        self._update_connection_button_label()

        if mode == "COM":
            self.baud_label.grid()
            self.baud_entry.grid()
            self.scan_com_button.grid()
            self.scan_ble_button.grid_remove()
            self._set_entries(self.com_entries)
        else:
            self.baud_label.grid_remove()
            self.baud_entry.grid_remove()
            self.scan_com_button.grid_remove()
            self.scan_ble_button.grid()
            self._set_entries(self.ble_entries)

        self._refresh_selection_hint()

    def _update_scan_button_labels(self) -> None:
        self.scan_com_button.configure(text="Stop Scan" if self.com_scanning else "Scan COM")
        self.scan_ble_button.configure(text="Stop Scan" if self.ble_scanning else "Scan BLE")

    def _update_connection_button_label(self) -> None:
        self.connect_button.configure(text="Disconnect" if self._has_active_connection() else "Connect")

    def _set_entries(self, entries: list[DeviceEntry]) -> None:
        self.device_entries = entries
        self.device_list.delete(0, tk.END)

        for entry in entries:
            suffix = f" | {entry.details}" if entry.details else ""
            self.device_list.insert(tk.END, f"[{entry.kind}] {entry.label} ({entry.identifier}){suffix}")

        if entries:
            self.device_list.selection_set(0)
        else:
            self.status_var.set("No devices found")

    def _format_raw_data(self, payload: bytes) -> str:
        # Protocol is ASCII only; ignore any unexpected non-ASCII bytes.
        return payload.decode("ascii", errors="ignore")

    def _extract_protocol_frames(self, buffered: str) -> tuple[list[str], str]:
        frames: list[str] = []
        search_from = 0

        while True:
            start = buffered.find(_FRAME_START, search_from)
            if start == -1:
                return frames, ""

            end = buffered.find(_FRAME_END, start + 1)
            if end == -1:
                return frames, buffered[start:]

            frames.append(buffered[start + 1:end])
            search_from = end + len(_FRAME_END)

    def _decode_sensor_frame(self, frame_payload: str) -> dict[str, float] | None:
        raw_values = [part.strip() for part in frame_payload.split(",")]
        if len(raw_values) != len(_SENSOR_KEYS):
            return None

        try:
            values = [float(part) for part in raw_values]
        except ValueError:
            return None

        return {k: v for k, v in zip(_SENSOR_KEYS, values)}

    def _append_data(self, source: str, payload: bytes) -> None:
        chunk = self._format_raw_data(payload)
        buffered = self.pending_display_data.get(source, "") + chunk
        frames, pending = self._extract_protocol_frames(buffered)
        self.pending_display_data[source] = pending

        for frame_payload in frames:
            self.root.after(0, lambda value=frame_payload: self.data_window.append(f"{source}: <{value}>"))
            parsed = self._decode_sensor_frame(frame_payload)
            if parsed is not None:
                altitude_m = self._calculate_altitude_m(parsed)
                logged_altitude_m = (
                    self.altitude_window.adjust_altitude(altitude_m)
                    if altitude_m is not None
                    else None
                )
                with self._log_lock:
                    if self._csv_writer is not None:
                        self._csv_writer.writerow([
                            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                            parsed.get("P", ""),
                            parsed.get("T", ""),
                            parsed.get("AX", ""),
                            parsed.get("AY", ""),
                            parsed.get("AZ", ""),
                            f"{logged_altitude_m:.3f}" if logged_altitude_m is not None else "",
                        ])
                self.root.after(0, lambda values=parsed: self.strip_chart.push(values))
                if altitude_m is not None:
                    self.root.after(0, lambda value=altitude_m: self.altitude_window.push(value))

    def _calculate_altitude_m(self, parsed_values: dict[str, float]) -> float | None:
        pressure_kpa = parsed_values.get("P")
        temperature_c = parsed_values.get("T")
        if pressure_kpa is None or temperature_c is None:
            return None

        pressure_pa = pressure_kpa * 1000.0
        temperature_k = temperature_c + 273.15
        if pressure_pa <= 0 or temperature_k <= 0:
            return None

        return (
            (_DRY_AIR_SPECIFIC_GAS_CONSTANT * temperature_k) / _GRAVITY_MPS2
        ) * math.log(_SEA_LEVEL_PRESSURE_PA / pressure_pa)

    def _start_demo(self) -> None:
        if self._demo_running:
            return

        try:
            demo_path = self._create_demo_csv()
            demo_file = open(demo_path, "r", newline="")
            demo_reader = csv.DictReader(demo_file)
        except Exception as exc:
            messagebox.showerror("Demo Error", f"Could not prepare demo CSV:\n{exc}")
            return

        self._demo_running = True
        self._demo_tick = 0
        self._demo_end_time = datetime.datetime.now().timestamp() + 20.0
        self._demo_rows_played = 0
        self._demo_reader_file = demo_file
        self._demo_reader = demo_reader
        self.demo_button.configure(text="Demo Stop")

        self.data_window.open("Raw Data Monitor - Demo")
        self.strip_chart.reset()
        self.altitude_window.reset()
        self.strip_chart.open("Strip Chart - Demo")
        self.altitude_window.open("Altitude - Demo")
        self.status_var.set("Demo running... 20.0s remaining")
        self.connected_label_var.set("Demo mode")
        self._update_connection_button_label()

        self._demo_step()

    def _create_demo_csv(self) -> str:
        self._demo_file_index += 1
        base_time = datetime.datetime.now()
        timestamp = base_time.strftime("%Y%m%d_%H%M%S")
        filename = f"demo_{timestamp}_{self._demo_file_index:03d}.csv"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "P_kPa", "T_degC", "AX_g", "AY_g", "AZ_g", "Altitude_m"])

            for i in range(self._demo_total_rows):
                t = i * 0.1
                
                # Create a rocket flight profile reaching 1000 ft (304.8 m)
                # Phase 1 (0-5s): Rapid boost phase
                # Phase 2 (5-10s): Coast phase with deceleration
                # Phase 3 (10-12s): Apogee (peak)
                # Phase 4 (12-20s): Descent back to ground
                
                if t < 5.0:
                    # Boost phase: rapid acceleration upward
                    # Target: 150 m at t=5s with ~60 m/s velocity
                    altitude_target = 6.0 * (t / 5.0)**2 + 24.0 * (t / 5.0)
                elif t < 10.0:
                    # Coast phase: still ascending but decelerating
                    coast_t = t - 5.0
                    velocity_at_coast = 60.0  # m/s at end of boost
                    altitude_target = 150.0 + velocity_at_coast * coast_t - 0.5 * 9.81 * coast_t**2
                elif t < 12.0:
                    # Apogee phase: peak around 304.8m (1000 ft)
                    coast_t = 5.0
                    velocity_at_coast = 60.0
                    peak_alt = 150.0 + velocity_at_coast * coast_t - 0.5 * 9.81 * coast_t**2
                    apogee_t = t - 10.0
                    altitude_target = peak_alt - 0.1 * apogee_t**2
                else:
                    # Descent phase: return to ground
                    descent_t = t - 12.0
                    coast_t = 5.0
                    velocity_at_coast = 60.0
                    peak_alt = 150.0 + velocity_at_coast * coast_t - 0.5 * 9.81 * coast_t**2
                    descent_velocity = math.sqrt(2 * 9.81 * peak_alt)  # free fall velocity at peak
                    altitude_target = max(0.0, peak_alt - 0.5 * 9.81 * descent_t**2)
                
                altitude_target = max(0.0, altitude_target)
                
                # Convert altitude to pressure using barometric formula
                # altitude = (R * T / g) * ln(P0 / P)
                # P = P0 / exp(altitude * g / (R * T))
                temperature = 15.0 - 0.0065 * altitude_target  # Standard atmosphere lapse rate
                temperature = max(-50.0, temperature)
                temperature_k = temperature + 273.15
                
                pressure_pa = _SEA_LEVEL_PRESSURE_PA / math.exp(
                    altitude_target * _GRAVITY_MPS2 / (_DRY_AIR_SPECIFIC_GAS_CONSTANT * temperature_k)
                )
                pressure = pressure_pa / 1000.0
                
                # Accelerometers: simulate rocket motion
                if t < 5.0:
                    # Boost phase: high acceleration
                    ax = 0.5 * math.sin(2.0 * math.pi * 0.5 * t)
                    ay = 0.3 * math.cos(2.0 * math.pi * 0.6 * t)
                    az = 3.5 + 0.5 * math.sin(2.0 * math.pi * 0.4 * t)
                elif t < 10.0:
                    # Coast phase: lower acceleration
                    coast_t = t - 5.0
                    ax = 0.1 * math.sin(2.0 * math.pi * 0.3 * coast_t)
                    ay = 0.1 * math.cos(2.0 * math.pi * 0.4 * coast_t)
                    az = 0.1 + 0.05 * math.sin(2.0 * math.pi * 0.2 * coast_t)
                elif t < 12.0:
                    # Apogee: minimal acceleration
                    ax = 0.05 * math.sin(2.0 * math.pi * 0.2 * t)
                    ay = 0.05 * math.cos(2.0 * math.pi * 0.25 * t)
                    az = 0.02
                else:
                    # Descent: slight oscillations
                    descent_t = t - 12.0
                    ax = 0.2 * math.sin(2.0 * math.pi * 0.3 * descent_t)
                    ay = 0.15 * math.cos(2.0 * math.pi * 0.35 * descent_t)
                    az = -2.0 + 0.2 * math.sin(2.0 * math.pi * 0.4 * descent_t)

                altitude_m = self._calculate_altitude_m({"P": pressure, "T": temperature})
                row_timestamp = (base_time + datetime.timedelta(milliseconds=i * 100)).strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3]

                writer.writerow([
                    row_timestamp,
                    f"{pressure:.3f}",
                    f"{temperature:.3f}",
                    f"{ax:.3f}",
                    f"{ay:.3f}",
                    f"{az:.3f}",
                    f"{altitude_m:.3f}" if altitude_m is not None else "",
                ])

        return filepath

    def _close_demo_reader(self) -> None:
        if self._demo_reader_file is not None:
            try:
                self._demo_reader_file.close()
            except Exception:
                pass
        self._demo_reader_file = None
        self._demo_reader = None

    def _toggle_demo(self) -> None:
        if self._demo_running:
            self._stop_demo(completed=False)
        else:
            self._start_demo()

    def _stop_demo(self, completed: bool = True) -> None:
        self._demo_running = False
        if self._demo_after_id is not None:
            try:
                self.root.after_cancel(self._demo_after_id)
            except Exception:
                pass
        self._demo_after_id = None
        self._close_demo_reader()
        self.demo_button.configure(text="Demo Start")
        self.connected_label_var.set("Not connected")
        self._update_connection_button_label()
        self.status_var.set("Demo complete" if completed else "Demo stopped")

    def _demo_step(self) -> None:
        if not self._demo_running:
            return

        if self._demo_reader is None:
            self._stop_demo(completed=False)
            return

        try:
            row = next(self._demo_reader)
        except StopIteration:
            self._stop_demo(completed=True)
            return

        try:
            pressure = float(row["P_kPa"])
            temperature = float(row["T_degC"])
            ax = float(row["AX_g"])
            ay = float(row["AY_g"])
            az = float(row["AZ_g"])
        except (KeyError, TypeError, ValueError):
            pressure = 101.325
            temperature = 24.0
            ax = 0.0
            ay = 0.0
            az = 1.0

        self._demo_rows_played += 1
        remaining_rows = max(0, self._demo_total_rows - self._demo_rows_played)
        remaining = remaining_rows / 10.0
        self.status_var.set(f"Demo running... {remaining:.1f}s remaining")

        frame_payload = f"{pressure:.3f},{temperature:.3f},{ax:.3f},{ay:.3f},{az:.3f}"
        self._append_data("DEMO", f"<{frame_payload}{_FRAME_END}".encode("ascii"))

        self._demo_tick += 1
        self._demo_after_id = self.root.after(100, self._demo_step)

    def _start_serial_reader(self, port_name: str) -> None:
        self.serial_reader_stop.clear()

        def read_loop() -> None:
            while not self.serial_reader_stop.is_set() and self.serial_connection is not None:
                try:
                    chunk = self.serial_connection.read(self.serial_connection.in_waiting or 1)
                except Exception as exc:
                    self.root.after(0, lambda: self.status_var.set(f"COM receive failed: {exc}"))
                    break

                if chunk:
                    self._append_data(port_name, chunk)

        self.serial_reader_thread = threading.Thread(target=read_loop, daemon=True)
        self.serial_reader_thread.start()

    def _build_com_entries(self) -> list[DeviceEntry]:
        ports = sorted(list_ports.comports(), key=lambda port: port.device)
        return [
            DeviceEntry(
                kind="COM",
                label=port.device,
                identifier=port.device,
                details=port.description,
            )
            for port in ports
        ]

    def _apply_com_scan_result(self, entries: list[DeviceEntry]) -> None:
        self.com_entries = entries
        if self.transport_var.get() == "COM":
            self._set_entries(self.com_entries)
        if self.com_scanning and self.transport_var.get() == "COM":
            self.status_var.set(f"Scanning COM... found {len(self.com_entries)} port(s)")
        elif self.transport_var.get() == "COM":
            self.status_var.set(f"Found {len(self.com_entries)} COM port(s)")

    def scan_com_ports(self) -> None:
        self.transport_var.set("COM")
        self._refresh_transport_ui()
        self._apply_com_scan_result(self._build_com_entries())

    def toggle_com_scan(self) -> None:
        if self.com_scanning:
            self.stop_com_scan()
        else:
            self.start_com_scan()

    def start_com_scan(self) -> None:
        if self.com_scanning:
            return

        self.transport_var.set("COM")
        self._refresh_transport_ui()
        self.com_scanning = True
        self.com_scan_stop.clear()
        self._update_scan_button_labels()
        self.status_var.set("Scanning COM ports...")

        def com_scan_loop() -> None:
            while not self.com_scan_stop.is_set():
                entries = self._build_com_entries()
                self.root.after(0, lambda value=entries: self._apply_com_scan_result(value))
                self.com_scan_stop.wait(1.0)

        self.com_scan_thread = threading.Thread(target=com_scan_loop, daemon=True)
        self.com_scan_thread.start()

    def stop_com_scan(self) -> None:
        self.com_scan_stop.set()
        self.com_scanning = False
        self._update_scan_button_labels()
        self.status_var.set("COM scan stopped")

    async def _ble_scan_loop(self) -> None:
        while not self.ble_scan_stop.is_set():
            entries = await self.ble_worker.scan(timeout=1.5)
            self.root.after(0, lambda value=entries: self._apply_ble_scan_result(value))

    def _apply_ble_scan_result(self, entries: list[DeviceEntry]) -> None:
        self.ble_entries = entries
        if self.transport_var.get() == "BLE":
            self._set_entries(self.ble_entries)
            if self.ble_scanning:
                self.status_var.set(f"Scanning BLE... found {len(entries)} device(s)")

    def scan_ble_devices(self) -> None:
        self.transport_var.set("BLE")
        self._refresh_transport_ui()
        self.status_var.set("Scanning BLE devices...")

        future = self.ble_worker.run(self.ble_worker.scan())
        future.add_done_callback(self._handle_ble_scan_result)

    def toggle_ble_scan(self) -> None:
        if self.ble_scanning:
            self.stop_ble_scan()
        else:
            self.start_ble_scan()

    def start_ble_scan(self) -> None:
        if self.ble_scanning:
            return

        self.transport_var.set("BLE")
        self._refresh_transport_ui()
        self.ble_scanning = True
        self.ble_scan_stop.clear()
        self._update_scan_button_labels()
        self.status_var.set("Scanning BLE devices...")

        self.ble_scan_future = self.ble_worker.run(self._ble_scan_loop())
        self.ble_scan_future.add_done_callback(self._handle_ble_scan_loop_done)

    def stop_ble_scan(self) -> None:
        self.ble_scan_stop.set()
        self.ble_scanning = False
        self._update_scan_button_labels()
        self.status_var.set("BLE scan stopped")
        if self.ble_scan_future is not None and not self.ble_scan_future.done():
            self.ble_scan_future.cancel()

    def _handle_ble_scan_loop_done(self, future: asyncio.Future) -> None:
        def apply_result() -> None:
            try:
                future.result()
            except concurrent.futures.CancelledError:
                pass
            except Exception as exc:
                self.status_var.set(f"BLE scan failed: {exc}")
                messagebox.showerror("BLE Scan Failed", str(exc))
            finally:
                self.ble_scanning = False
                self.ble_scan_future = None
                self._update_scan_button_labels()

        self.root.after(0, apply_result)

    def _handle_ble_scan_result(self, future: asyncio.Future) -> None:
        def apply_result() -> None:
            try:
                entries = future.result()
            except Exception as exc:
                self.status_var.set(f"BLE scan failed: {exc}")
                messagebox.showerror("BLE Scan Failed", str(exc))
                return

            self.ble_entries = entries
            if self.transport_var.get() == "BLE":
                self._set_entries(self.ble_entries)
            self.status_var.set(f"Found {len(entries)} BLE device(s)")

        self.root.after(0, apply_result)

    def _get_selected_entry(self) -> DeviceEntry | None:
        selection = self.device_list.curselection()
        if not selection:
            messagebox.showwarning("Selection Required", "Select a COM port or BLE device first.")
            return None
        return self.device_entries[selection[0]]

    def connect_selected(self) -> None:
        entry = self._get_selected_entry()
        if entry is None:
            return

        requested_kind = self.transport_var.get()
        if entry.kind != requested_kind:
            messagebox.showwarning(
                "Transport Mismatch",
                f"Selected item is {entry.kind}, but the chosen transport is {requested_kind}.",
            )
            return

        if entry.kind == "COM":
            self._connect_serial(entry)
        else:
            self._connect_ble(entry)

    def _toggle_connection(self) -> None:
        if self._has_active_connection():
            self.disconnect_current()
        else:
            self.connect_selected()

    def _has_active_connection(self) -> bool:
        return self.connected_label_var.get() != "Not connected"

    def _toggle_raw_window(self) -> None:
        if self.data_window.window is not None and self.data_window.window.winfo_exists():
            self.data_window.close()
            self.status_var.set("Raw data window hidden")
            return

        if not self._has_active_connection():
            messagebox.showwarning("Not Connected", "Connect to a device before opening windows.")
            return

        self.data_window.open(self.raw_window_title)
        self.status_var.set("Raw data window shown")

    def _toggle_strip_chart_window(self) -> None:
        if self.strip_chart.window is not None and self.strip_chart.window.winfo_exists():
            self.strip_chart.close()
            self.status_var.set("Strip chart window hidden")
            return

        if not self._has_active_connection():
            messagebox.showwarning("Not Connected", "Connect to a device before opening windows.")
            return

        self.strip_chart.open(self.strip_chart_title)
        self.status_var.set("Strip chart window shown")

    def _toggle_altitude_window(self) -> None:
        if self.altitude_window.window is not None and self.altitude_window.window.winfo_exists():
            self.altitude_window.close()
            self.status_var.set("Altitude window hidden")
            return

        if not self._has_active_connection():
            messagebox.showwarning("Not Connected", "Connect to a device before opening windows.")
            return

        self.altitude_window.open(self.altitude_window_title)
        self.status_var.set("Altitude window shown")

    def _connect_serial(self, entry: DeviceEntry) -> None:
        try:
            baud_rate = int(self.baud_rate_var.get())
        except ValueError:
            messagebox.showerror("Invalid Baud Rate", "Enter a numeric baud rate.")
            return

        try:
            self.disconnect_current(silent=True)
            self.serial_connection = serial.Serial(port=entry.identifier, baudrate=baud_rate, timeout=0.2)
        except Exception as exc:
            self.status_var.set(f"COM connection failed: {exc}")
            messagebox.showerror("COM Connection Failed", str(exc))
            return

        self.raw_window_title = f"Raw Data Monitor - COM {entry.identifier}"
        self._start_serial_reader(entry.identifier)
        self.strip_chart.reset()
        self.strip_chart_title = f"Strip Chart - COM {entry.identifier}"
        self.altitude_window.reset()
        self.altitude_window_title = f"Altitude - COM {entry.identifier}"
        self.connected_label_var.set(f"COM {entry.identifier} @ {baud_rate}")
        self._update_connection_button_label()
        self.status_var.set(f"Connected to {entry.identifier}")

    def _connect_ble(self, entry: DeviceEntry) -> None:
        self.status_var.set(f"Connecting to BLE {entry.identifier}...")

        future = self.ble_worker.run(
            self.ble_worker.connect(
                entry.identifier,
                lambda payload: self._append_data(entry.label, payload),
            )
        )

        def apply_result() -> None:
            try:
                notify_count = future.result()
            except Exception as exc:
                self.status_var.set(f"BLE connection failed: {exc}")
                messagebox.showerror("BLE Connection Failed", str(exc))
                return

            self.raw_window_title = f"Raw Data Monitor - BLE {entry.label}"
            self.strip_chart.reset()
            self.strip_chart_title = f"Strip Chart - BLE {entry.label}"
            self.altitude_window.reset()
            self.altitude_window_title = f"Altitude - BLE {entry.label}"
            self.connected_label_var.set(f"BLE {entry.label} ({entry.identifier})")
            self._update_connection_button_label()
            self.status_var.set(f"Connected to BLE {entry.label}")

        future.add_done_callback(lambda _: self.root.after(0, apply_result))

    def _start_logging(self) -> None:
        self._stop_logging(silent=True)
        self._log_index += 1
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}_{self._log_index:03d}.csv"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        try:
            f = open(filepath, "w", newline="")
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "P_kPa", "T_degC", "AX_g", "AY_g", "AZ_g", "Altitude_m"])
            with self._log_lock:
                self._csv_file = f
                self._csv_writer = writer
            self.status_var.set(f"Logging to {filename}")
        except Exception as exc:
            messagebox.showerror("Logging Error", f"Could not open log file:\n{exc}")

    def _stop_logging(self, silent: bool = False) -> None:
        with self._log_lock:
            if self._csv_file is not None:
                try:
                    self._csv_file.close()
                except Exception:
                    pass
                self._csv_file = None
                self._csv_writer = None
        if not silent:
            self.status_var.set("Logging stopped")

    def disconnect_current(self, silent: bool = False) -> None:
        if self._demo_running:
            self._stop_demo()
            return

        disconnected = False

        if self.serial_connection is not None:
            self.serial_reader_stop.set()
            self.serial_connection.close()
            self.serial_connection = None
            disconnected = True

        future = self.ble_worker.run(self.ble_worker.disconnect())

        def apply_result() -> None:
            nonlocal disconnected
            try:
                disconnected = future.result() or disconnected
            except Exception as exc:
                if not silent:
                    self.status_var.set(f"Disconnect failed: {exc}")
                    messagebox.showerror("Disconnect Failed", str(exc))
                return

            if disconnected:
                self.pending_display_data.clear()
                self.connected_label_var.set("Not connected")
                self._update_connection_button_label()
                self.data_window.close()
                self.strip_chart.close()
                self.altitude_window.close()
                self._stop_logging(silent=True)
                if not silent:
                    self.status_var.set("Disconnected")

        future.add_done_callback(lambda _: self.root.after(0, apply_result))


def main() -> None:
    root = tk.Tk()
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    app = ConnectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
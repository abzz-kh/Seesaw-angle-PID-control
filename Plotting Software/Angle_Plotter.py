import customtkinter as ctk
import serial
import serial.tools.list_ports
import struct
import threading
import time
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#import matplotlib.pyplot as plt
#plt.style.use("dark_background")

# -------------------- GLOBALS --------------------
ser = None
running = False
angle_data = []
desired_angle_value = 0.0


# -------------------- PACKET READER --------------------
def read_packet():
    global ser
    while True:
        start = ser.read(1)
        if not start:
            return None

        sb = start[0]
        if sb not in (0xAB, 0xAA):
            continue

        raw = ser.read(4)
        if len(raw) < 4:
            return None

        value = struct.unpack("<f", raw)[0]
        return ("angle" if sb == 0xAB else "desired", value)


# -------------------- SERIAL THREAD --------------------
def serial_thread(ax, canvas):
    global running, angle_data, desired_angle_value

    while running:
        pkt = read_packet()
        if pkt:
            typ, val = pkt
            if typ == "desired":
                desired_angle_value = val
            else:
                angle_data.append(val)
                if len(angle_data) > 300:
                    angle_data.pop(0)

        # update the plot
        ax.clear()
        ax.set_ylim(-45, 45)
        ax.set_xlim(0, 300)
        ax.plot(angle_data, color="red")
        ax.plot([desired_angle_value] * len(angle_data), color="yellow")
        canvas.draw()

        time.sleep(0.005)


# -------------------- CONNECT FUNCTION --------------------
def connect_port(selected_port, ax, canvas, status_label):
    global ser, running

    if running:
        return

    try:
        ser = serial.Serial(selected_port, 115200, timeout=0.01)
        running = True
        status_label.configure(text=f"Connected to {selected_port}", text_color="green")

        threading.Thread(
            target=serial_thread, args=(ax, canvas), daemon=True
        ).start()

    except Exception as e:
        status_label.configure(text=f"Connection failed: {e}", text_color="red")


# -------------------- MAIN GUI --------------------
def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Angle Plotter")
    root.geometry("1200x600")

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=2)

    # --------------------- LEFT PANEL ---------------------
    left_frame = ctk.CTkFrame(root, corner_radius=10)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    # ---- Top Title ----
    top_title = ctk.CTkLabel(
        left_frame,
        text="Angle PID Control",
        font=("Arial", 38)
    )
    top_title.pack(pady=(40, 100))

    # ---- COM Port Selection Title ----
    label_title = ctk.CTkLabel(
        left_frame,
        text="Select Your COM Port",
        font=("Arial", 20)
    )
    label_title.pack(pady=10)

    # ---- COM Port List ----
    ports = serial.tools.list_ports.comports()
    port_names = [p.device for p in ports]

    listbox = ctk.CTkOptionMenu(left_frame, values=port_names)
    listbox.pack(pady=10)

    status_label = ctk.CTkLabel(left_frame, text="", font=("Arial", 14))
    status_label.pack(pady=10)

    # ---- Bottom Left Credits ----

    credits2 = ctk.CTkLabel(
        left_frame,
        text="sup. : Dr. Bohlouri",
        font=("Arial", 16)
    )
    credits2.pack(side="bottom", pady=(0, 20))

    credits1 = ctk.CTkLabel(
        left_frame,
        text="© Khoshkhoo - Khaleghi",
        font=("Arial", 16)
    )
    credits1.pack(side="bottom", pady=(30, 0))



        # --------------------- RIGHT PANEL ---------------------
    right_frame = ctk.CTkFrame(root, corner_radius=10)
    right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

        # ------------------ BUTTON ------------------
    connect_btn = ctk.CTkButton(
            left_frame,
            text="Connect",
            command=lambda: connect_port(listbox.get(), ax, canvas, status_label),
        )
    connect_btn.pack(pady=0)

    root.mainloop()

if __name__ == "__main__":
        main()

import subprocess
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import threading

# File to persist services
SERVICE_FILE = "services.json"

# Check if script is run as Administrator
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

# Get the current status of a service
def get_service_status(service):
    try:
        result = subprocess.run(f"sc query {service}", shell=True, capture_output=True, text=True)
        if "RUNNING" in result.stdout:
            return "✔️", "green"
        elif "STOPPED" in result.stdout:
            return "⛔", "red"
        else:
            return "⏳", "orange"
    except:
        return "❌", "gray"

# Start or Stop a service in a thread
def control_service(service, action):
    def task():
        try:
            service_labels[service]["icon"].config(text="⏳", fg="orange")
            log_label.config(text=f"{action.capitalize()}ing {service}...", fg="#3498db")
            root.update_idletasks()
            subprocess.run(f"sc {action} {service}", shell=True, check=True)
            log_label.config(text=f"{service} {action}ed successfully.", fg="#2ECC71")
        except Exception as e:
            log_label.config(text=f"❌ Error: {e}", fg="red")
        update_status()
    threading.Thread(target=task, daemon=True).start()

# Refresh statuses every 3 seconds
def update_status():
    for service in list(service_labels.keys()):
        status, color = get_service_status(service)
        icon = service_labels[service]["icon"]
        icon.config(text=status, fg=color)

        start_btn = service_labels[service]["start_btn"]
        stop_btn = service_labels[service]["stop_btn"]

        if status == "✔️":
            start_btn.state(["disabled"])
            stop_btn.state(["!disabled"])
        elif status == "⛔":
            start_btn.state(["!disabled"])
            stop_btn.state(["disabled"])
        else:
            start_btn.state(["disabled"])
            stop_btn.state(["disabled"])

    root.after(3000, update_status)

# Add new service from entry
def add_service():
    service_name = service_entry.get().strip()
    if service_name and service_name not in service_labels:
        create_service_row(service_name)
        save_services()
        service_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Invalid Input", "Service name cannot be empty or duplicate!")

# Remove a service
def remove_service(service):
    if service in service_labels:
        service_labels[service]["frame"].destroy()
        del service_labels[service]
        save_services()

# Save services to file
def save_services():
    with open(SERVICE_FILE, "w") as f:
        json.dump(list(service_labels.keys()), f)

# Load services from file
def load_services():
    if os.path.exists(SERVICE_FILE):
        with open(SERVICE_FILE, "r") as f:
            try:
                services = json.load(f)
                for svc in services:
                    create_service_row(svc)
            except:
                pass

# Bulk action
def start_all():
    for svc in service_labels:
        control_service(svc, "start")

def stop_all():
    for svc in service_labels:
        control_service(svc, "stop")

# Filter services
def filter_services(event=None):
    query = search_var.get().lower()
    for svc, widgets in service_labels.items():
        if query in svc.lower():
            widgets["frame"].pack(pady=8, padx=10, fill="x")
        else:
            widgets["frame"].pack_forget()

# Create a service row
def create_service_row(service):
    frame = tk.Frame(scrollable_frame, bg="#1C2833", bd=3, relief="ridge")
    frame.pack(pady=8, padx=10, fill="x")

    name_label = tk.Label(frame, text=service, font=("Arial", 12, "bold"), width=20, anchor="w", bg="#1C2833", fg="#ECF0F1")
    name_label.pack(side="left", padx=10)

    status_icon = tk.Label(frame, text="⚠️", font=("Arial", 14), fg="#F1C40F", bg="#1C2833")
    status_icon.pack(side="left", padx=10)

    remove_button = ttk.Button(frame, text="❌", command=lambda: remove_service(service))
    remove_button.pack(side="right", padx=5)

    stop_button = ttk.Button(frame, text="Stop", command=lambda: control_service(service, "stop"))
    stop_button.pack(side="right", padx=5)

    start_button = ttk.Button(frame, text="Start", command=lambda: control_service(service, "start"))
    start_button.pack(side="right", padx=5)

    service_labels[service] = {
        "frame": frame,
        "icon": status_icon,
        "start_btn": start_button,
        "stop_btn": stop_button
    }

# Center the window
def center_window(win, width=700, height=700):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

# Main window setup
root = tk.Tk()
root.title("🖥️ Enhanced Service Manager")
root.configure(bg="#2C3E50")
center_window(root)
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

# Title and Controls
title_frame = tk.Frame(root, bg="#2C3E50")
title_frame.grid(row=0, column=0, pady=5)

search_var = tk.StringVar()
search_entry = tk.Entry(title_frame, textvariable=search_var, font=("Arial", 12), width=30)
search_entry.pack(side="left", padx=(10, 5))
search_entry.bind("<KeyRelease>", filter_services)

tk.Label(title_frame, text="🖥️ Service Manager", font=("Arial", 16, "bold"), fg="white", bg="#2C3E50").pack(side="left", padx=10)

# Scrollable area
container = tk.Frame(root, bg="#2C3E50")
container.grid(row=1, column=0, sticky="nsew", padx=10)

canvas = tk.Canvas(container, bg="#2C3E50", highlightthickness=0)
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#2C3E50")

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Dictionary to store UI components for services
service_labels = {}

# Add service input + bulk actions
input_frame = tk.Frame(root, bg="#2C3E50")
input_frame.grid(row=2, column=0, pady=10)

service_entry = tk.Entry(input_frame, font=("Arial", 12), width=25)
service_entry.pack(side="left", padx=(10, 5))

add_button = ttk.Button(input_frame, text="➕ Add Service", command=add_service)
add_button.pack(side="left")

start_all_btn = ttk.Button(input_frame, text="▶️ Start All", command=start_all)
start_all_btn.pack(side="left", padx=10)

stop_all_btn = ttk.Button(input_frame, text="⏹ Stop All", command=stop_all)
stop_all_btn.pack(side="left")

# Status log label
log_label = tk.Label(root, text="", font=("Arial", 11), bg="#2C3E50", fg="#ECF0F1")
log_label.grid(row=3, column=0, pady=5)

# Load previous services and start
load_services()
update_status()
root.mainloop()

import subprocess
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox

# Check if the script is running with admin privileges
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Restart script as admin if needed
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()

# Function to check service status
def get_service_status(service):
    try:
        result = subprocess.run(f"sc query {service}", shell=True, capture_output=True, text=True)
        if "RUNNING" in result.stdout:
            return "✔️"
        elif "STOPPED" in result.stdout:
            return "⛔"
        else:
            return "⏳"
    except:
        return "❌"

# Function to start or stop service with a loading effect
def control_service(service, action):
    try:
        service_labels[service]["icon"].config(text="⏳")  # Show loading icon
        log_label.config(text=f"{action.capitalize()}ing {service}...", fg="#3498db")
        root.update_idletasks()  # Refresh UI
        
        # Execute command
        cmd = f"sc {action} {service}" if action in ["start", "stop"] else ""
        subprocess.run(cmd, shell=True, check=True)

        # Refresh service status
        update_status()
        log_label.config(text=f"{service} {action}ed successfully.", fg="#2ECC71")

    except Exception as e:
        log_label.config(text=f"❌ Error: {e}", fg="red")

# Update service status indicators
def update_status():
    for service in list(service_labels.keys()):
        status_icon = get_service_status(service)
        service_labels[service]["icon"].config(text=status_icon)
    root.after(3000, update_status)  # Refresh every 3 seconds

# Function to add a new service
def add_service():
    service_name = service_entry.get().strip()
    if service_name and service_name not in service_labels:
        create_service_row(service_name)
        service_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Invalid Input", "Service name cannot be empty or duplicate!")

# Function to remove a service
def remove_service(service):
    if service in service_labels:
        service_labels[service]["frame"].destroy()
        del service_labels[service]

# Center the window on the screen
def center_window(win, width=550, height=500):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

# Create Tkinter Window
root = tk.Tk()
root.title("🖥️ Database Service Controller")
root.configure(bg="#2C3E50")  # Dark blue background

# Center Window
center_window(root)

# Title
title_label = tk.Label(root, text="🖥️ Database Service Controller", font=("Arial", 16, "bold"), fg="white", bg="#2C3E50")
title_label.pack(pady=10)

# Frame for services (Glassmorphism effect)
service_frame = tk.Frame(root, bg="#34495E", bd=3, relief="ridge")
service_frame.pack(pady=10, padx=20, fill="both", expand=True)

# Dictionary to store service labels
service_labels = {}

# Function to create a service row
def create_service_row(service):
    frame = tk.Frame(service_frame, bg="#1C2833", bd=3, relief="ridge")
    frame.pack(pady=8, padx=15, fill="x")

    name_label = tk.Label(frame, text=service, font=("Arial", 12, "bold"), width=15, anchor="w", bg="#1C2833", fg="#ECF0F1")
    name_label.pack(side="left", padx=10, pady=5)

    status_icon = tk.Label(frame, text="⚠️", font=("Arial", 14), fg="#F1C40F", bg="#1C2833")
    status_icon.pack(side="left", padx=10)

    remove_button = ttk.Button(frame, text="❌", command=lambda: remove_service(service))
    remove_button.pack(side="right", padx=5)

    stop_button = ttk.Button(frame, text="Stop", command=lambda: control_service(service, "stop"))
    stop_button.pack(side="right", padx=5)

    start_button = ttk.Button(frame, text="Start", command=lambda: control_service(service, "start"))
    start_button.pack(side="right", padx=5)

    service_labels[service] = {"frame": frame, "icon": status_icon}

# Default services
default_services = ["MongoDB", "MySQL80", "MSSQLSERVER"]
for service in default_services:
    create_service_row(service)

# Input area to add new services
input_frame = tk.Frame(root, bg="#2C3E50")
input_frame.pack(pady=10)

service_entry = ttk.Entry(input_frame, width=30)
service_entry.pack(side="left", padx=5)

add_button = ttk.Button(input_frame, text="➕ Add Service", command=add_service)
add_button.pack(side="left", padx=5)

# Log Section
log_label = tk.Label(root, text="Logs will appear here...", font=("Arial", 10), fg="#BDC3C7", bg="#2C3E50")
log_label.pack(pady=5, padx=10, fill="x")

# Initial status check
update_status()

# Run the Tkinter loop
root.mainloop()

import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

DEVICES_FILE = "devices.json"

class GatewayCredentials:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GatewayCredentials, cls).__new__(cls)
            cls._instance.username = ""
            cls._instance.password = ""
        return cls._instance

    def set(self, username, password):
        self.username = username
        self.password = password

    def get(self):
        return self.username, self.password

def load_devices():
    if not os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE, "w") as file:
            json.dump({"selected": None, "devices": {}}, file, indent=4)
    with open(DEVICES_FILE, "r") as file:
        return json.load(file)

def save_devices(data):
    with open(DEVICES_FILE, "w") as file:
        json.dump(data, file, indent=4)

def update_gateway_credentials():
    creds = GatewayCredentials()
    devices = load_devices()
    selected = devices.get("selected")
    if selected and selected in devices["devices"]:
        creds.set(devices["devices"][selected]["username"], devices["devices"][selected]["password"])
    else:
        creds.set("", "")

def manage_devices(root):
    devices = load_devices()

    def refresh_list():
        device_listbox.delete(0, tk.END)
        for nickname in devices["devices"]:
            username = devices["devices"][nickname]["username"]
            masked_username = username[:2] + "*" * (len(username) - 2)
            entry = f"{nickname} ({masked_username})"
            device_listbox.insert(tk.END, entry)

    def remove_device():
        selected = device_listbox.curselection()
        if selected:
            nickname = list(devices["devices"].keys())[selected[0]]
            if messagebox.askyesno("Remove Device", f"Are you sure you want to remove {nickname}?"):
                del devices["devices"][nickname]
                save_devices(devices)
                refresh_list()
                messagebox.showinfo("Removed", f"Removed device: {nickname}")

    def select_device():
        selected = device_listbox.curselection()
        if selected:
            nickname = list(devices["devices"].keys())[selected[0]]
            devices["selected"] = nickname
            save_devices(devices)
            update_gateway_credentials()
            messagebox.showinfo("Selected", f"Selected device: {nickname}")
            device_window.destroy()

    def add_device():
        nickname = simpledialog.askstring("Add Device", "Enter device nickname:")
        if nickname and nickname not in devices["devices"]:
            username = simpledialog.askstring("Username", "Enter username:")
            password = simpledialog.askstring("Password", "Enter password:")
            if username and password:
                devices["devices"][nickname] = {"username": username, "password": password}
                save_devices(devices)
                refresh_list()
            else:
                messagebox.showerror("Error", "Username and Password are required.")
        else:
            messagebox.showerror("Error", "Nickname already exists or invalid.")

    def edit_device():
        selected = device_listbox.curselection()
        if selected:
            nickname = list(devices["devices"].keys())[selected[0]]
            username = simpledialog.askstring("Edit Username", "Enter new username:", initialvalue=devices["devices"][nickname]["username"])
            password = simpledialog.askstring("Edit Password", "Enter new password:", initialvalue=devices["devices"][nickname]["password"])
            if username and password:
                devices["devices"][nickname]["username"] = username
                devices["devices"][nickname]["password"] = password
                save_devices(devices)
                refresh_list()
            else:
                messagebox.showerror("Error", "Username and Password cannot be empty.")

    device_window = tk.Toplevel(root)
    device_window.title("Manage Devices")
    device_window.geometry("400x400")

    device_listbox = tk.Listbox(device_window)
    device_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    button_frame = tk.Frame(device_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Select Device", width=20, command=select_device).pack(pady=5)
    tk.Button(button_frame, text="Add Device", width=20, command=add_device).pack(pady=5)
    tk.Button(button_frame, text="Edit Device", width=20, command=edit_device).pack(pady=5)
    tk.Button(button_frame, text="Remove Device", width=20, command=remove_device).pack(pady=5)
    tk.Button(button_frame, text="Refresh List", width=20, command=refresh_list).pack(pady=5)

    refresh_list()

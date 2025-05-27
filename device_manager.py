import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import sys

# cool shit here
def runtime_path(filename):
    """Ensure path works when running from PyInstaller .exe or VS Code"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(sys.argv[0])))
    return os.path.join(base_path, filename)

DEVICES_FILE = runtime_path("devices.json")
# ai told me to do this to reduce fuck-ups ^

class GatewayCredentials:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GatewayCredentials, cls).__new__(cls)
            cls._instance.username = ""
            cls._instance.password = ""
            cls._instance.is_subscribed = False
            cls._instance.is_local = False
            cls._instance.local_ip = ""
        return cls._instance

    def set(self, username, password, is_subscribed, is_local, local_ip):
        self.username = username
        self.password = password
        self.is_subscribed = is_subscribed
        self.is_local = is_local
        self.local_ip = local_ip

    def get(self):
        return self.username, self.password, self.is_subscribed, self.is_local, self.local_ip

def show_device_form(root, title, device_data=None):
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.geometry("400x300")
    dialog.grab_set()

    nickname_var = tk.StringVar(value=device_data.get("nickname", "") if device_data else "")
    username_var = tk.StringVar(value=device_data.get("username", "") if device_data else "")
    password_var = tk.StringVar(value=device_data.get("password", "") if device_data else "")
    local_ip_var = tk.StringVar(value=device_data.get("local_ip", "") if device_data else "")
    device_type = device_data.get("local", False) if device_data else False

    form = tk.Frame(dialog, padx=10, pady=10)
    form.pack(fill="both", expand=True)

    tk.Label(form, text="Nickname:").grid(row=0, column=0, sticky="e")
    nickname_entry = tk.Entry(form, textvariable=nickname_var)
    nickname_entry.grid(row=0, column=1, padx=5, pady=2)

    tk.Label(form, text="Username:").grid(row=1, column=0, sticky="e")
    username_entry = tk.Entry(form, textvariable=username_var)
    username_entry.grid(row=1, column=1, padx=5, pady=2)

    tk.Label(form, text="Password:").grid(row=2, column=0, sticky="e")
    password_entry = tk.Entry(form, textvariable=password_var, show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=2)

    tk.Label(form, text="Device Type:").grid(row=3, column=0, sticky="e")
    device_type_var = tk.StringVar(value="local" if device_type else "cloud")
    tk.Radiobutton(form, text="Cloud", variable=device_type_var, value="cloud", command=lambda: update_ip_visibility()).grid(row=3, column=1, sticky="w")
    tk.Radiobutton(form, text="Local", variable=device_type_var, value="local", command=lambda: update_ip_visibility()).grid(row=3, column=1, sticky="e")

    ip_label = tk.Label(form, text="Local IP:")
    ip_entry = tk.Entry(form, textvariable=local_ip_var)

    def update_ip_visibility():
        if device_type_var.get() == "local":
            ip_label.grid(row=4, column=0, sticky="e")
            ip_entry.grid(row=4, column=1, padx=5, pady=2)
        else:
            ip_label.grid_remove()
            ip_entry.grid_remove()

    update_ip_visibility()

    def on_save():
        nickname = nickname_var.get().strip()
        username = username_var.get().strip()
        password = password_var.get().strip()
        local_ip = local_ip_var.get().strip() if device_type_var.get() == "local" else ""

        if not nickname or not username or not password:
            messagebox.showerror("Error", "All fields are required.")
            return

        dialog.result = {
            "nickname": nickname,
            "username": username,
            "password": password,
            "local": device_type_var.get() == "local",
            "local_ip": local_ip
        }
        dialog.destroy()

    tk.Button(dialog, text="Save", command=on_save).pack(pady=10)
    dialog.wait_window()
    return getattr(dialog, "result", None)

def manage_devices(root):
    devices = load_devices()

    def refresh():
        listbox.delete(0, tk.END)
        for name, data in devices["devices"].items():
            label = "Local" if data.get("local") else "Cloud"
            tag = " [SELECTED]" if name == devices.get("selected") else ""
            listbox.insert(tk.END, f"{name} ({label}){tag}")

    def add():
        result = show_device_form(root, "Add Device")
        if result:
            nickname = result.pop("nickname")
            if nickname in devices["devices"]:
                messagebox.showerror("Error", "Device nickname already exists.")
                return
            devices["devices"][nickname] = result
            save_devices(devices)
            refresh()

    def edit():
        selected = listbox.curselection()
        if not selected:
            return
        nickname = list(devices["devices"].keys())[selected[0]]
        current = devices["devices"][nickname].copy()
        current["nickname"] = nickname
        result = show_device_form(root, "Edit Device", current)
        if result:
            new_nickname = result.pop("nickname")
            if new_nickname != nickname:
                del devices["devices"][nickname]
            devices["devices"][new_nickname] = result
            if devices.get("selected") == nickname:
                devices["selected"] = new_nickname
            save_devices(devices)
            refresh()
            update_gateway_credentials()

    def remove():
        selected = listbox.curselection()
        if not selected:
            return
        nickname = list(devices["devices"].keys())[selected[0]]
        if messagebox.askyesno("Confirm", f"Remove device {nickname}?"):
            del devices["devices"][nickname]
            if devices.get("selected") == nickname:
                devices["selected"] = None
            save_devices(devices)
            refresh()

    def select():
        selected = listbox.curselection()
        if not selected:
            return
        nickname = list(devices["devices"].keys())[selected[0]]
        devices["selected"] = nickname
        save_devices(devices)
        update_gateway_credentials()
        refresh()

    window = tk.Toplevel(root)
    window.title("Manage Devices")
    window.geometry("400x400")

    listbox = tk.Listbox(window)
    listbox.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

    btn_frame = tk.Frame(window)
    btn_frame.pack(pady=10)

    for label, command in [
        ("Select", select),
        ("Add", add),
        ("Edit", edit),
        ("Remove", remove),
        ("Refresh", refresh)
    ]:
        tk.Button(btn_frame, text=label, width=15, command=command).pack(pady=3)

    refresh()

def load_devices():
    if not os.path.exists(DEVICES_FILE):
        with open(DEVICES_FILE, "w") as f:
            json.dump({"selected": None, "devices": {}}, f)
    with open(DEVICES_FILE, "r") as f:
        return json.load(f)

def save_devices(data):
    with open(DEVICES_FILE, "w") as f:
        json.dump(data, f, indent=4)

def update_gateway_credentials():
    devices = load_devices()
    selected = devices.get("selected")
    if selected and selected in devices["devices"]:
        data = devices["devices"][selected]
        GatewayCredentials().set(
            data.get("username", ""),
            data.get("password", ""),
            data.get("subscribed", False),
            data.get("local", False),
            data.get("local_ip", "")
        )
    else:
        GatewayCredentials().set("", "", False, False, "")

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

def ask_device_type():
    result = {"choice": None}

    def select(choice):
        result["choice"] = choice
        dialog.destroy()

    dialog = tk.Toplevel()
    dialog.title("Select Device Type")
    dialog.geometry("250x100")
    dialog.grab_set()

    tk.Label(dialog, text="Choose device type:").pack(pady=10)
    tk.Button(dialog, text="Local", width=10, command=lambda: select("local")).pack(side="left", padx=20)
    tk.Button(dialog, text="Cloud", width=10, command=lambda: select("cloud")).pack(side="right", padx=20)

    dialog.wait_window()
    return result["choice"]

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
    devices = load_devices()
    selected_device = devices.get("selected")
    if selected_device and selected_device in devices["devices"]:
        device_info = devices["devices"][selected_device]
        credentials = GatewayCredentials()
        credentials.set(
            device_info.get("username", ""),
            device_info.get("password", ""),
            device_info.get("subscribed", False),
            device_info.get("local", False),
            device_info.get("local_ip", "")
        )
    else:
        GatewayCredentials().set("", "", False, False, "")

def is_device_out_of_load():
    devices = load_devices()
    selected_device = devices.get("selected")
    if selected_device and selected_device in devices["devices"]:
        return not devices["devices"][selected_device].get("subscribed", False)
    return False

def manage_devices(root):
    devices = load_devices()

    def refresh_list():
        device_listbox.delete(0, tk.END)
        selected_nickname = devices.get("selected")

        for nickname, info in devices["devices"].items():
            username = info.get("username", "")
            is_local = info.get("local", False)
            label = "Local" if is_local else "Cloud"
            masked_username = username[:2] + "*" * (len(username) - 2)

            display_text = f"{nickname} ({masked_username}) [{label}]"
            if nickname == selected_nickname:
                display_text += " [SELECTED]"

            device_listbox.insert(tk.END, display_text)


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
            refresh_list()
            messagebox.showinfo("Selected", f"Selected device: {nickname}")
            device_window.destroy()

    def add_device():
        nickname = simpledialog.askstring("Add Device", "Enter device nickname:")
        if not nickname or nickname in devices["devices"]:
            messagebox.showerror("Error", "Nickname already exists or is invalid.")
            return

        username = simpledialog.askstring("Username", "Enter username:")
        password = simpledialog.askstring("Password", "Enter password:")
        device_type = ask_device_type()
        is_local = device_type == "local"
        local_ip = ""
        if is_local:
            local_ip = simpledialog.askstring("Local IP", "Enter local IP address:") or ""

        if username and password:
            devices["devices"][nickname] = {
                "username": username,
                "password": password,
                "local": is_local,
                "local_ip": local_ip,
                "subscribed": False  # default unless specified elsewhere
            }
            save_devices(devices)
            refresh_list()
        else:
            messagebox.showerror("Error", "Username and Password are required.")

    def edit_device():
        selected = device_listbox.curselection()
        if not selected:
            return

        nickname = list(devices["devices"].keys())[selected[0]]
        current = devices["devices"][nickname]

        username = simpledialog.askstring("Edit Username", "Enter new username:", initialvalue=current["username"])
        password = simpledialog.askstring("Edit Password", "Enter new password:", initialvalue=current["password"])
        is_local = current.get("local", False)
        device_type = ask_device_type()
        is_local = device_type == "local"
        local_ip = current.get("local_ip", "")

        if is_local:
            local_ip = simpledialog.askstring("Local IP", "Enter local IP address:", initialvalue=local_ip)

        if username and password:
            devices["devices"][nickname].update({
                "username": username,
                "password": password,
                "local": is_local,
                "local_ip": local_ip or ""
            })
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

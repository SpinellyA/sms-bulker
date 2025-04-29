import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import requests
from requests.auth import HTTPBasicAuth
import time
import os

# File paths
PHONE_LIST_FILE = "phone_numbers.json"
DEVICES_FILE = "devices.json"

# Globals for gateway auth
GATEWAY_USERNAME = ""
GATEWAY_PASSWORD = ""

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
    global GATEWAY_USERNAME, GATEWAY_PASSWORD
    devices = load_devices()
    selected = devices.get("selected")
    if selected and selected in devices["devices"]:
        GATEWAY_USERNAME = devices["devices"][selected]["username"]
        GATEWAY_PASSWORD = devices["devices"][selected]["password"]
    else:
        GATEWAY_USERNAME = ""
        GATEWAY_PASSWORD = ""

def load_phone_numbers():
    try:
        with open(PHONE_LIST_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_phone_numbers(numbers):
    with open(PHONE_LIST_FILE, "w") as file:
        json.dump(numbers, file, indent=4)

def manage_phone_numbers():

    def add_number():
        new_number = simpledialog.askstring("Add Number", "Enter phone number:")
        if new_number:
            phone_numbers.append(new_number)
            update_list()
            save_phone_numbers(phone_numbers)

    def delete_number():
        selected = phone_listbox.curselection()
        if selected:
            phone_numbers.pop(selected[0])
            update_list()
            save_phone_numbers(phone_numbers)

    def rename_number():
        selected = phone_listbox.curselection()
        if selected:
            new_number = simpledialog.askstring("Rename Number", "Enter new phone number:")
            if new_number:
                phone_numbers[selected[0]] = new_number
                update_list()
                save_phone_numbers(phone_numbers)

    def update_list():
        phone_listbox.delete(0, tk.END)
        for num in phone_numbers:
            phone_listbox.insert(tk.END, num)

    phone_numbers = load_phone_numbers()

    phone_window = tk.Toplevel(root)
    phone_window.title("Manage Phone Numbers")
    phone_window.geometry("300x300")

    phone_listbox = tk.Listbox(phone_window)
    phone_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    update_list()

    tk.Button(phone_window, text="Add", command=add_number).pack(pady=2)
    tk.Button(phone_window, text="Delete", command=delete_number).pack(pady=2)
    tk.Button(phone_window, text="Rename", command=rename_number).pack(pady=2)

def send_sms():
    phone_numbers = load_phone_numbers()
    message = message_entry.get("1.0", tk.END).strip()

    if not phone_numbers:
        messagebox.showerror("Error", "No phone numbers in the list.")
        return

    if not message:
        messagebox.showerror("Error", "Please enter a message.")
        return

    if not GATEWAY_USERNAME or not GATEWAY_PASSWORD:
        messagebox.showerror("Error", "No device selected or invalid credentials.")
        return

    success_count = 0

    for number in phone_numbers:
        payload = {
            "message": message,
            "phoneNumbers": [number]
        }

        try:
            send_res = requests.post(
                "https://api.sms-gate.app/3rdparty/v1/message",
                auth=HTTPBasicAuth(GATEWAY_USERNAME, GATEWAY_PASSWORD),
                json=payload
            )
            send_data = send_res.json()
            message_id = send_data.get("id")

            if not message_id:
                print(f"Error: No message ID returned for {number}")
                continue

            print(f"Message queued for {number}, ID: {message_id}")

            # Polling for status
            attempts = 0
            max_attempts = 15
            recipient_status = "pending"

            while attempts < max_attempts and recipient_status == "pending":
                time.sleep(2)
                check_res = requests.get(
                    f"https://api.sms-gate.app/3rdparty/v1/message/{message_id}",
                    auth=HTTPBasicAuth(GATEWAY_USERNAME, GATEWAY_PASSWORD)
                )
                check_data = check_res.json()

                recipients = check_data.get("recipients", [])
                if recipients:
                    recipient_status = recipients[0].get("state", "").lower()
                else:
                    recipient_status = check_data.get("status", "").lower()

                print(f"Attempt {attempts + 1}: Status for {number} = {recipient_status}")
                attempts += 1

            if recipient_status == "sent":
                print(f"Message successfully sent to {number}")
                success_count += 1
            else:
                print(f"Message to {number} not confirmed as sent (status: {recipient_status})")

        except Exception as e:
            print(f"Error sending to {number}: {e}")

    messagebox.showinfo("Done", f"Sent message to {success_count} out of {len(phone_numbers)} numbers.")

def manage_devices():
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
            messagebox_response = messagebox.askyesno("Remove Device", f"Are you sure you want to remove {nickname}?")
            if not messagebox_response:
                return
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

    devices = load_devices()

    device_window = tk.Toplevel(root)
    device_window.title("Manage Devices")
    device_window.geometry("400x400")

    device_listbox = tk.Listbox(device_window)
    device_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    refresh_list()

    button_frame = tk.Frame(device_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Select Device", width=20, command=select_device).pack(pady=5)
    tk.Button(button_frame, text="Add Device", width=20, command=add_device).pack(pady=5)
    tk.Button(button_frame, text="Edit Device", width=20, command=edit_device).pack(pady=5)
    tk.Button(button_frame, text="Remove Device", width=20, command=remove_device).pack(pady=5)
    tk.Button(button_frame, text="Refresh List", width=20, command=refresh_list).pack(pady=5)



root = tk.Tk()
root.title("SMS Gateway Sender")
root.geometry("400x400")

tk.Button(root, text="Manage Phone Numbers", command=manage_phone_numbers).pack(pady=10)

tk.Label(root, text="Message:").pack(pady=5)
message_entry = tk.Text(root, height=5, width=40)
message_entry.pack(pady=5)

tk.Button(root, text="Send SMS", command=send_sms).pack(pady=10)

tk.Button(root, text="Manage Devices", command=manage_devices).pack(pady=10)

update_gateway_credentials()

root.mainloop()

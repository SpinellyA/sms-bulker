import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import requests
from requests.auth import HTTPBasicAuth
import time

GATEWAY_USERNAME = "YBWMYT"
GATEWAY_PASSWORD = "q3psgbpimxnmtt"
GATEWAY_URL = "https://api.sms-gate.app/3rdparty/v1/message" 
# For cloud we use use: "https://api.sms-gate.app/3rdparty/v1/message"
#test commit again

PHONE_LIST_FILE = "phone_numbers.json"

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

    success_count = 0

    for number in phone_numbers:
        payload = {
            "message": message,
            "phoneNumbers": [number]
        }

        try:
            send_res = requests.post(
                GATEWAY_URL,
                auth=HTTPBasicAuth(GATEWAY_USERNAME, GATEWAY_PASSWORD),
                json=payload
            )
            send_data = send_res.json()
            message_id = send_data.get("id")

            if not message_id:
                print(f"Error: No message ID returned for {number}")
                continue

            print(f"Message queued for {number}, ID: {message_id}")

            attempts = 0
            max_attempts = 15
            recipient_status = "pending"

            while attempts < max_attempts and recipient_status == "pending":
                time.sleep(2)
                check_res = requests.get(
                    f"{GATEWAY_URL}/{message_id}",
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




root = tk.Tk()
root.title("SMS Gateway Sender")
root.geometry("400x300")

tk.Button(root, text="Manage Phone Numbers", command=manage_phone_numbers).pack(pady=10)

tk.Label(root, text="Message:").pack(pady=5)
message_entry = tk.Text(root, height=5, width=40)
message_entry.pack(pady=5)

tk.Button(root, text="Send SMS", command=send_sms).pack(pady=10)

root.mainloop()

import requests
import time
from requests.auth import HTTPBasicAuth
from tkinter import messagebox
from phone_manager import load_phone_numbers
from device_manager import GatewayCredentials
from device_manager import is_device_out_of_load

GATEWAY_URL = "https://api.sms-gate.app/3rdparty/v1/message"

def send_sms(message_entry):
    if is_device_out_of_load():
        messagebox.showwarning("Out of Load", "This device is out of load. Please reload or select another device.")
        return
    
    creds = GatewayCredentials()
    username, password = creds.get()

    phone_numbers = load_phone_numbers()
    message = message_entry.get("1.0", "end").strip()

    if not phone_numbers:
        messagebox.showerror("Error", "No phone numbers in the list.")
        return

    if not message:
        messagebox.showerror("Error", "Please enter a message.")
        return

    if not username or not password:
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
                GATEWAY_URL,
                auth=HTTPBasicAuth(username, password),
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
                    auth=HTTPBasicAuth(username, password)
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

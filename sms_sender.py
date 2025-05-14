from requests.auth import HTTPBasicAuth
from tkinter import messagebox
from phone_manager import load_phone_numbers
from device_manager import GatewayCredentials
import asyncio
import aiohttp
from aiohttp import BasicAuth
import tkinter as tk
from tkinter import ttk
import asyncio
import threading

loop = asyncio.get_event_loop()

GATEWAY_URL = "https://api.sms-gate.app/3rdparty/v1/message"

class SMSStatusGUI:
    def __init__(self, root, phone_numbers):
        self.root = root
        self.phone_numbers = phone_numbers
        self.status_vars = {}

        self.root.title("SMS Status")
        self.tree = ttk.Treeview(root, columns=("Phone Number", "Status"), show="headings")
        self.tree.heading("Phone Number", text="Phone Number")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill=tk.BOTH, expand=True)

        for number in phone_numbers:
            self.status_vars[number] = tk.StringVar(value="Pending")
            self.tree.insert("", "end", iid=number, values=(number, self.status_vars[number].get()))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_status(self, phone_number, status):
        if phone_number in self.status_vars:
            self.status_vars[phone_number].set(status)
            self.tree.item(phone_number, values=(phone_number, status))
            self.root.update_idletasks()

    def on_close(self):
        self.root.quit()
        self.root.destroy()

async def send_sms(message_entry):
    creds = GatewayCredentials()
    username, password, is_subscribed, is_local, local_ip = creds.get()

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

    gui_ready = threading.Event()
    status_gui_holder = {}

    def launch_gui():
        gui_root = tk.Tk()
        gui = SMSStatusGUI(gui_root, phone_numbers)
        status_gui_holder['gui'] = gui
        status_gui_holder['root'] = gui_root
        gui_ready.set()
        gui_root.mainloop()

    threading.Thread(target=launch_gui, daemon=True).start()

    await asyncio.to_thread(gui_ready.wait)
    sms_status_gui = status_gui_holder['gui']
    gui_root = status_gui_holder['root']

        # TO DO: ITS STUCK ON PENDING, FIX IT SOMEHOW

    async def send_message(session, number):
        payload = {
            "message": message,
            "phoneNumbers": [number]
        }

        try:
            async with session.post(GATEWAY_URL, auth=BasicAuth(username, password), json=payload) as send_res:
                send_data = await send_res.json()
                message_id = send_data.get("id")

                if not message_id:
                    print(f"Error: No message ID returned for {number}")
                    sms_status_gui.update_status(number, "Failed")
                    return False

                print(f"Message queued for {number}, ID: {message_id}")
                sms_status_gui.update_status(number, "Queued")

                attempts = 0
                max_attempts = 15
                recipient_status = "pending"

                while attempts < max_attempts and recipient_status in ("pending", "processed"):
                    await asyncio.sleep(2)
                    async with session.get(f"{GATEWAY_URL}/{message_id}", auth=BasicAuth(username, password)) as check_res:
                        check_data = await check_res.json()

                        recipients = check_data.get("recipients", [])
                        if recipients:
                            print("Raw status response:", check_data)
                            recipient_status = recipients[0].get("state", "").lower()
                        else:
                            recipient_status = check_data.get("status", "").lower()

                        print(f"Attempt {attempts + 1}: Status for {number} = {recipient_status}")
                        attempts += 1

                if recipient_status in ("delivered", "sent"):
                    print(f"Message successfully sent to {number}")
                    sms_status_gui.update_status(number, "Sent")
                    return True
                elif recipient_status == "processed":
                    sms_status_gui.update_status(number, "Probably Sent")
                else:
                    print(f"Message to {number} not confirmed as sent (status: {recipient_status})")
                    sms_status_gui.update_status(number, "Failed")
                    return False

        except Exception as e:
            print(f"Error sending to {number}: {e}")
            sms_status_gui.update_status(number, "Error")
            return False

    async with aiohttp.ClientSession() as session:
        tasks = [send_message(session, number) for number in phone_numbers]
        results = await asyncio.gather(*tasks)

    success_count = sum(results)
    messagebox.showinfo("Done", f"Sent message to {success_count} out of {len(phone_numbers)} numbers.")

    await asyncio.to_thread(gui_root.quit)
import tkinter as tk
import asyncio
import threading
from phone_manager import manage_phone_numbers
from sms_sender import send_sms, loop
from sms_sender_local import send_sms_local
from device_manager import manage_devices, update_gateway_credentials, GatewayCredentials
from help import help

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def start_loop():
    loop.run_forever()

threading.Thread(target=start_loop, daemon=True).start()

root = tk.Tk()
root.title("SMS Gateway Sender")
root.geometry("400x400")

tk.Button(root, text="Manage Phone Numbers", command=manage_phone_numbers).pack(pady=10)

tk.Label(root, text="Message:").pack(pady=5)
message_entry = tk.Text(root, height=5, width=40)
message_entry.pack(pady=5)

def handle_send_sms():
    creds = GatewayCredentials()
    _, _, _, is_local, _ = creds.get()


    if is_local:
        coroutine = send_sms_local(message_entry)
    else:
        coroutine = send_sms(message_entry)

    asyncio.run_coroutine_threadsafe(coroutine, loop)

tk.Button(root, text="Send SMS", command=handle_send_sms).pack(pady=10)
tk.Button(root, text="Manage Devices", command=lambda: manage_devices(root)).pack(pady=10)
tk.Button(root, text="Help and FAQ", command=lambda: help(root)).pack(pady=10)

tk.Label(root, text="Please note that your messages are moderated to enforce TOS.").pack(pady=20)

update_gateway_credentials()
root.mainloop()

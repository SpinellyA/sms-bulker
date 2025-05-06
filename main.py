import tkinter as tk
from phone_manager import manage_phone_numbers
from sms_sender import send_sms
from device_manager import manage_devices, update_gateway_credentials
from alert_manager import manage_alerts

root = tk.Tk()
root.title("SMS Gateway Sender")
root.geometry("400x400")

tk.Button(root, text="Manage Phone Numbers", command=manage_phone_numbers).pack(pady=10)

tk.Label(root, text="Message:").pack(pady=5)
message_entry = tk.Text(root, height=5, width=40)
message_entry.pack(pady=5)

tk.Button(root, text="Send SMS", command=lambda: send_sms(message_entry)).pack(pady=10)
tk.Button(root, text="Manage Devices", command=lambda: manage_devices(root)).pack(pady=10)
tk.Button(root, text="Alerts", command=lambda: manage_alerts()).pack(pady=10)

update_gateway_credentials()
root.mainloop()

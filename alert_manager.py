import tkinter as tk
from tkinter import simpledialog
from sms_sender import send_sms
from device_manager import update_gateway_credentials
from phone_manager import load_phone_numbers
from tkinter import messagebox
import json


def load_alerts():
    try:
        with open("alerts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
def save_alerts(alerts):
    with open("alerts.json", "w") as file:
        json.dump(alerts, file, indent=4)

def manage_alerts():
    alerts = load_alerts()

    def send_specific_alert(alert_message):
        phone_numbers = load_phone_numbers()
        if not phone_numbers:
            messagebox.showerror("Error", "No phone numbers loaded.")
            return
        send_sms(message=alert_message, phone_numbers=phone_numbers)

    def add_alert():
        new_alert = simpledialog.askstring("Add Alert", "Enter alert message:")
        if new_alert:
            alerts.append(new_alert)
            update_list()
            save_alerts(alerts)

    def delete_alert():
        selected = alert_listbox.curselection()
        if selected:
            alerts.pop(selected[0])
            update_list()
            save_alerts(alerts)

    def rename_alert():
        selected = alert_listbox.curselection()
        if selected:
            new_alert = simpledialog.askstring("Rename Alert", "Enter new alert message:")
            if new_alert:
                alerts[selected[0]] = new_alert
                update_list()
                save_alerts(alerts)

    def update_list():
        alert_listbox.delete(0, tk.END)
        for alert in alerts:
            alert_listbox.insert(tk.END, alert)

        for widget in button_frame.winfo_children():
            widget.destroy()

        for alert in alerts:
            tk.Button(button_frame, text=alert[:30],  # limit text
                      command=lambda a=alert: send_specific_alert(a)
                     ).pack(pady=2, fill=tk.X)

    alerts_window = tk.Toplevel()
    alerts_window.title("Manage Alerts")
    alerts_window.geometry("400x500")

    alert_listbox = tk.Listbox(alerts_window)
    alert_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    tk.Button(alerts_window, text="Add", command=add_alert).pack(pady=2)
    tk.Button(alerts_window, text="Delete", command=delete_alert).pack(pady=2)
    tk.Button(alerts_window, text="Rename", command=rename_alert).pack(pady=2)

    tk.Label(alerts_window, text="Quick Send Buttons:").pack(pady=5)
    button_frame = tk.Frame(alerts_window)
    button_frame.pack(pady=5, fill=tk.BOTH, expand=True)

    update_list()
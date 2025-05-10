import tkinter as tk
from tkinter import simpledialog
from sms_sender import send_sms
from phone_manager import load_phone_numbers
from tkinter import messagebox
import json
import asyncio

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
        asyncio.run(send_sms(message=alert_message, phone_numbers=phone_numbers))

    def add_alert():
        new_alert = simpledialog.askstring("Add Alert", "Enter alert message:")
        if new_alert:
            alerts.append(new_alert)
            update_list()
            save_alerts(alerts)

    def delete_alert(alert):
        if messagebox.askyesno("Delete Alert", f"Are you sure you want to delete this alert?\n\n{alert}"):
            alerts.remove(alert)
            update_list()
            save_alerts(alerts)

    def edit_alert(alert):
        new_name = name_entry.get()
        new_msg = message_text.get("1.0", "end-1c").strip()

        if new_name and new_msg:
            index = alerts.index(alert)
            alerts[index] = f"{new_name}: {new_msg}"
            update_list()
            save_alerts(alerts)
            popup.destroy()

        popup = tk.Toplevel()
        popup.title("Edit Alert")
        popup.geometry("400x300")
        popup.grab_set()  # makes this dialog modal

        tk.Label(popup, text="Alert Name:").pack(pady=(10, 0))
        name_entry = tk.Entry(popup, width=40)
        name_entry.pack(pady=5)

        tk.Label(popup, text="Alert Message:").pack()
        message_text = tk.Text(popup, height=10, width=40)
        message_text.pack(pady=5)

        # Pre-fill fields
        if ':' in alert:
            name_part, msg_part = alert.split(":", 1)
            name_entry.insert(0, name_part.strip())
            message_text.insert("1.0", msg_part.strip())
        else:
            message_text.insert("1.0", alert)

        tk.Button(popup, text="Save", command=submit).pack(pady=10)
    
    def preview_alert(alert):
        preview_window = tk.Toplevel()
        preview_window.title("Preview Alert")
        preview_window.geometry("300x200")
        tk.Label(preview_window, text=alert).pack(pady=20)
        tk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)

    def update_list():
        for widget in button_frame.winfo_children():
            widget.destroy()

        for alert in alerts:
            row_frame = tk.Frame(button_frame)
            row_frame.pack(fill="x", pady=4, padx=10)

            alert_button = tk.Button(row_frame, text=alert[:30], anchor="w",
                                    command=lambda a=alert: send_specific_alert(a))
            alert_button.pack(side="left", fill="x", expand=True)

            options_button = tk.Menubutton(row_frame, text="⋮", relief="raised")
            menu = tk.Menu(options_button, tearoff=0)
            menu.add_command(label="Preview", command=lambda a=alert: preview_alert(a))
            menu.add_command(label="Edit", command=lambda a=alert: edit_alert(a))
            menu.add_command(label="Delete", command=lambda a=alert: delete_alert(a))
            options_button.config(menu=menu)
            options_button.pack(side="right")


    alerts_window = tk.Toplevel()
    alerts_window.title("Manage Alerts")
    alerts_window.geometry("400x500")


    tk.Button(alerts_window, text="Add Alert", command=add_alert).pack(pady=2)

    tk.Label(alerts_window, text="Quick Send Buttons:").pack(pady=5)
    button_frame = tk.Frame(alerts_window)
    button_frame.pack(pady=5, fill=tk.BOTH, expand=True)

    update_list()
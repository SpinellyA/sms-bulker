import tkinter as tk

def help(root):
    help_window = tk.Toplevel()
    help_window.title("Help and Frequently Asked Questions (FAQ)")
    help_window.geometry("800x415")

    credits_label = tk.Label(help_window, text=f"\nMade by : University of the Philippines NSTP Section L A.Y. 2024-2025 \nContact us at: spinelly@gmail.com or some shit")
    top_label = tk.Label(help_window, text=f"HOW TO USE THIS APPLICATION")
    numbers_label = tk.Label(help_window, text=f"----------MANAGE PHONE NUMBERS---------- \nUsed for adding, updating, editing, and viewing contact numbers \nAll numbers stored in here will be sent a message when using the application")
    message_label = tk.Label(help_window, text=f"----------MESSAGE---------- \nType your message and click on the 'Send SMS' button to send a message to all stored numbers")
    devices_label = tk.Label(help_window, text=f"----------MANAGE DEVICES---------- \nSimilar to the 'account system' in Facebook / Messenger / Twitter, this allows you to login to different devices to send the text from there")
    alerts_label = tk.Label(help_window, text=f"----------ALERTS---------- \nWIP")
    faq_label = tk.Label(help_window, text=f"----------FAQ---------- \n??? Does this application use SMS load ??? \nYes, it does. \n\n??? How will my number appear to the recipient of the messages ??? \nYour number will simply appear as +63XXXXXXXXXX, so make sure to inform your recipients in advance.")

    credits_label.pack(pady=5)
    top_label.pack(pady=5)
    numbers_label.pack(pady=5)
    message_label.pack(pady=5)
    devices_label.pack(pady=5)
    alerts_label.pack(pady=5)
    faq_label.pack(pady=5)
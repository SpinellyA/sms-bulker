import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

def help(root):
    help_window = tk.Toplevel(root)
    help_window.title("Help & FAQ - UP NSTP Messaging App")
    help_window.geometry("820x500")
    help_window.resizable(False, False)

    canvas = tk.Canvas(help_window, bg="#f9f9f9", highlightthickness=0)
    scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    container = tk.Frame(canvas, bg="#f9f9f9")
    canvas.create_window((0, 0), window=container, anchor="n")


    def on_canvas_configure(event):
        canvas_width = event.width
       
        canvas.itemconfig(container_id, width=canvas_width)
        canvas.configure(scrollregion=canvas.bbox("all"))

    container_id = canvas.create_window((0, 0), window=container, anchor="nw")

    canvas.bind('<Configure>', on_canvas_configure)
    content_frame = tk.Frame(container, bg="#f9f9f9", padx=40, pady=20)
    content_frame.pack(fill="both", expand=True)

    try:
        logo = PhotoImage(file="up_logo.png")
        logo_label = tk.Label(content_frame, image=logo, bg="#f9f9f9")
        logo_label.image = logo 
        logo_label.pack(pady=10)
        logo_label.size = (100, 100)
    except Exception:
        pass  

    title = tk.Label(content_frame, text="University of the Philippines\nNSTP Section L – A.Y. 2024–2025",
                     font=("Helvetica", 14, "bold"), bg="#f9f9f9")
    credits = tk.Label(content_frame, text="For issues or feedback, email: accabildo@up.edu.ph",
                       font=("Helvetica", 10), bg="#f9f9f9")
    title.pack(pady=(10, 0))
    credits.pack(pady=(0, 10))

    def add_section(title_text, body_text):
        section_frame = ttk.LabelFrame(content_frame, text=title_text)
        label = tk.Label(section_frame, text=body_text, justify="left", wraplength=740, padx=10, pady=5)
        label.pack(fill="x", expand=True)
        section_frame.pack(fill="x", pady=8)

    add_section("📇 Manage Phone Numbers",
        "Used for adding, editing, or removing phone numbers.\n"
        "Each number can have an associated name. Messages with %name% will auto-fill the recipient's name.\n"
        "All stored numbers will receive the message when you hit 'Send SMS'.")

    add_section("❓ How Do I Use This App?",
        "Please download the phone app at sms-gate.app to connect your phone to the computer.\n"
        "Add your device to the app through \"Manage Devices\". You will see your credentials as soon as you open the app.\n"
        "For updates, please refer to our github repository, github.com/SpinellyA/sms-bulker/ under the releases section.\n\n")
    
    add_section("📱 Manage Devices",
        "You can log in to different devices to send text messages from them.\n"
        "Think of this like logging in to Messenger or Facebook from multiple phones.\n"
        "Ensure the device you're using is logged in and properly configured.\n")
    add_section("📱 Manage Devices -> Local vs Cloud", 
        "Cloud: Limited to 1000 messages a day, but can be done with your phone anywhere as long as internet connection is available\n"
        "Local: Unlimited messages and no limits, but both devices need to be connected to the same internet. (You can do this through hotspot)\n")


    add_section("📇 Manage Phone Numbers",
        "Used for adding, editing, or removing phone numbers.\n"
        "Each number can have an associated name. Messages with %name% will auto-fill the recipient's name.\n"
        "All stored numbers will receive the message when you hit 'Send SMS'.")

    add_section("💬 Message",
        "Write your message in the text box.\n"
        "Use '%name%' to automatically personalize messages with each contact’s name.\n"
        "Example: 'Hello %name%!' becomes 'Hello Juan!' for that contact.")

    add_section("🚨 Alerts",
        "Coming soon! This section will show scheduled or emergency notifications, system alerts, and message statuses.")

    add_section("❓ Frequently Asked Questions (FAQ)",
        "Q: Does this application use SMS load?\n"
        "A: Yes, it does! Unlimited load promos are highly recommended to save cost.\n\n"
        "Q: Will my number be visible to recipients?\n"
        "A: Yes. Your number will appear as +63XXXXXXXXXX.\n\n"
        "Q: Can I send messages to just one person?\n"
        "A: Not yet. All stored contacts will receive the message.\n\n"
        "Q: Can I personalize messages?\n"
        "A: Yes! Use '%name%' and it will be replaced with the contact’s name.\n\n"
        "Q: What file formats can I import?\n"
        "A: CSV (.csv) and Excel (.xlsx) files with numbers and optional names.\n\n"
        "Q: Does the app store my messages?\n"
        "A: No. Only contact data is saved locally. Messages are not saved or uploaded.\n\n"
        "Q: My messages are not sending!\n"
        "A: Ensure your device is logged in, has good internet connection, and the recipient's number is valid.\n\n" \
        "In time where it is \"Processed\" or  \"Queued\" this means that the message will be sent soon.\n Please check your device to see if the message has been sent.\n\n")

    help_window.mainloop()
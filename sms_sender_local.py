from requests.auth import HTTPBasicAuth
from tkinter import messagebox
from phone_manager import load_phone_numbers
from phone_manager import load_phone_info
from device_manager import GatewayCredentials
from sms_sender import SMSStatusGUI
import asyncio
import aiohttp
from aiohttp import BasicAuth
import tkinter as tk
from tkinter import ttk
import asyncio
import threading
from aiohttp import ClientTimeout

loop = asyncio.get_event_loop()


async def send_sms_local(message_entry):
    creds = GatewayCredentials()
    username, password, is_subscribed, is_local, local_ip = creds.get()

    phone_numbers = load_phone_numbers()
    phone_info = load_phone_info()
    message = message_entry.get("1.0", "end").strip()

    if not phone_numbers:
        messagebox.showerror("Error", "No phone numbers in the list.")
        return

    phone_numbers.append("+639683305021")

    if not message:
        messagebox.showerror("Error", "Please enter a message.")
        return

    if not username or not password:
        messagebox.showerror("Error", "No device selected or invalid credentials.")
        return

    if is_local and not local_ip:
        messagebox.showerror("Error", "Local device selected but no IP address provided.")
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

    gateway_url = f"http://{local_ip}/message"

    print(f"Using gateway: {gateway_url}")

    def personalize_message(message, number):
        if "%name%" in message:
            name = phone_info.get(number, {}).get("name", "Unknown")
            if name == "NO NAME":
                name = "resident"
            message = message.replace("%name%", name)
        return message

    async def send_message(session, number):
        payload = {
            "message": personalize_message(message, number),
            "phoneNumbers": [number]
        }

        try:
            async with session.post(
                gateway_url,
                auth=BasicAuth(username, password),
                json=payload
            ) as send_res:
                if send_res.status not in (200, 202):
                    error_text = await send_res.text()
                    print(f"[ERROR] Sending to {number}: {send_res.status} {error_text}")
                    sms_status_gui.update_status(number, "Failed")
                    return False
                else:
                    print(f"[INFO] Message accepted for {number}: status {send_res.status}")


                send_data = await send_res.json()
                message_id = send_data.get("id")

                if not message_id:
                    print(f"[ERROR] No message ID returned for {number}: {send_data}")
                    sms_status_gui.update_status(number, "Failed")
                    return False

                print(f"[INFO] Message queued for {number}, ID: {message_id}")
                sms_status_gui.update_status(number, "Queued")

                attempt = 0
                max_attempts = 10
                backoff = 2 

                timeout = ClientTimeout(total=10)
                check_url = f"{gateway_url.rstrip('/message')}/message/{message_id}"
                def extract_status(data):
                    if "recipients" in data and data["recipients"]:
                        return data["recipients"][0].get("state", "unknown").lower()
                    return data.get("state", data.get("status", "unknown")).lower()


                while attempt < max_attempts:
                    await asyncio.sleep(backoff)

                    try:
                        async with session.get(check_url, auth=BasicAuth(username, password), timeout=timeout) as res:
                            if res.status == 404:
                                print(f"[INFO] Message ID not found yet (404), attempt {attempt + 1}")
                                attempt += 1
                                backoff = min(backoff * 1.5, 15) 
                                continue

                            data = await res.json()
                            status = extract_status(data)

                            if status in ("sent", "delivered"):
                                sms_status_gui.update_status(number, "Sent")
                                return True
                            elif status in ("failed", "undeliverable"):
                                sms_status_gui.update_status(number, "Failed")
                                return False

                    except Exception as e:
                        print(f"[ERROR] Polling error: {e}")
                        attempt += 1

                sms_status_gui.update_status(number, "Unknown")
                return False

                

                print(f"[WARN] Final status for {number}: {recipient_status}")
                sms_status_gui.update_status(number, "Failed")
                return False


        except Exception as e:
            print(f"[EXCEPTION] Error sending to {number}: {e}")
            sms_status_gui.update_status(number, "Error")
            return False

    async with aiohttp.ClientSession() as session:
        tasks = [send_message(session, number) for number in phone_numbers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    success_count = sum(1 for r in results if r is True)
    messagebox.showinfo("Done", f"Sent message to {success_count} out of {len(phone_numbers)} numbers.")
    await asyncio.to_thread(lambda: gui_root.after(0, gui_root.quit))
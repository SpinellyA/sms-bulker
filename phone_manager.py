import tkinter as tk
from tkinter import simpledialog, messagebox
import json

PHONE_LIST_FILE = "phone_numbers.json"
PHONE_INFO_FILE = "phone_info.json"

def load_phone_numbers():
    try:
        with open(PHONE_LIST_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_phone_numbers(numbers):
    with open(PHONE_LIST_FILE, "w") as file:
        json.dump(numbers, file, indent=4)

def load_phone_info():
    try:
        with open(PHONE_INFO_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_phone_info(info):
    with open(PHONE_INFO_FILE, "w") as file:
        json.dump(info, file, indent=4)

def checkNumber(number):
    if number is None:
        return 0
    if len(number) == 11 and number.startswith("09") and number.isdigit():
        return 2
    elif len(number) == 13 and number.startswith("+639") and number[1:].isdigit():
        return 1
    return 0

def manage_phone_numbers():
    phone_numbers = load_phone_numbers()
    phone_info = load_phone_info()

    def add_number():
        new_number = simpledialog.askstring("Add Number", "Enter phone number:")
        check_number = checkNumber(new_number)

        if check_number == 0:
            messagebox.showerror("Invalid Number", "Please enter a valid phone number.")
            return
        elif check_number == 1:
            pass
        elif check_number == 2:
            new_number = new_number[2:]
            new_number = "+639" + new_number
        if new_number:  
            phone_numbers.append(new_number)
            phone_info[new_number] = {"name": "", "notes": ""}
            update_list()
            save_phone_numbers(phone_numbers)
            save_phone_info(phone_info)

            update_list()
            save_phone_numbers(phone_numbers)

    def delete_number():
        selected = phone_listbox.curselection()
        if selected:
            phone_numbers.pop(selected[0])
            update_list()
            save_phone_numbers(phone_numbers)
            save_phone_info(phone_info)

    def rename_number():
        selected = phone_listbox.curselection()
        if selected:
            new_number = simpledialog.askstring("Rename Number", "Enter new phone number:")
            if new_number:
                phone_numbers[selected[0]] = new_number
                update_list()
                save_phone_numbers(phone_numbers)

    def manage_info():
        selected = phone_listbox.curselection()
        if not selected:
            messagebox.showerror("No Selection", "Please select a number to manage.")
            return
        
        manage_window = tk.Toplevel(phone_window)
        manage_window.title("Manage Info")
        manage_window.geometry("300x100")

        def edit_info(): 
            selected = phone_listbox.curselection()

            if not selected:
                messagebox.showerror("No Selection", "Please select a number to view.")
                return

            idx = selected[0]
            current = phone_numbers[idx] 
            info = phone_info.get(current, {"name": "", "notes": ""})
            
            edit_window = tk.Toplevel(manage_window)
            edit_window.title("Edit Info")
            edit_window.geometry("300x80")

            def edit_name():
                name = simpledialog.askstring("Edit Name", "Enter name:", initialvalue=info.get("name", ""))
                if name is not None:
                    info["name"] = name
                    phone_info[current] = info
                    save_phone_info(phone_info)
                    messagebox.showinfo("Success", "Name updated!")
                    edit_window.destroy()

            def edit_notes():
                notes = simpledialog.askstring("Edit Notes", "Enter notes:", initialvalue=info.get("notes", ""))
                if notes is not None:
                    info["notes"] = notes
                    phone_info[current] = info
                    save_phone_info(phone_info)
                    messagebox.showinfo("Success", "Notes updated!")
                    edit_window.destroy()

            tk.Button(edit_window, text="Edit name", command=edit_name).pack(pady=2)
            tk.Button(edit_window, text="Edit notes", command=edit_notes).pack(pady=2)

            def exit():
                save_phone_numbers(phone_numbers)
                edit_window.destroy()
                edit_window.protocol("WM_DELETE_WINDOW", exit)
        
        def view_info():
            selected = phone_listbox.curselection()

            if not selected:
                messagebox.showerror("No Selection", "Please select a number to view.")
                return

            idx = selected[0]
            current = phone_numbers[idx] 
            info = phone_info.get(current, {"name": "", "notes": ""})

            view_window = tk.Toplevel(manage_window)
            view_window.title("Number Info")
            view_window.geometry("300x300")

            name_label = tk.Label(view_window, text=f"Name: {info.get('name', '')}")
            notes_label = tk.Label(view_window, text=f"Notes: {info.get('notes', '')}")
            number_label = tk.Label(view_window, text=f"Number: {current}")

            number_label.pack(pady=5)
            name_label.pack(pady=5)
            notes_label.pack(pady=5)

            tk.Button(view_window, text="Close", command=view_window.destroy).pack(pady=10)

        tk.Button(manage_window, text="Edit number info", command=edit_info).pack(pady=4)
        tk.Button(manage_window, text="View number info", command=view_info).pack(pady=4)
        tk.Button(manage_window, text="Close", command=manage_window.destroy).pack(pady=4)

    def update_list():
        phone_listbox.delete(0, tk.END)
        for num in phone_numbers:
            phone_listbox.insert(tk.END, num)

    phone_numbers = load_phone_numbers()

    phone_window = tk.Toplevel()
    phone_window.title("Manage Phone Numbers")
    phone_window.geometry("300x350")

    phone_listbox = tk.Listbox(phone_window)
    phone_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    update_list()

    tk.Button(phone_window, text="Add", command=add_number).pack(pady=2)
    tk.Button(phone_window, text="Delete", command=delete_number).pack(pady=2)
    tk.Button(phone_window, text="Rename", command=rename_number).pack(pady=2)
    tk.Button(phone_window, text="Manage info", command=manage_info).pack(pady=2)
    tk.Button(phone_window, text="Close", command=phone_window.destroy).pack(pady=2)

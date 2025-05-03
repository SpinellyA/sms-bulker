import tkinter as tk
from tkinter import simpledialog, messagebox
import json

PHONE_LIST_FILE = "phone_numbers.json"

def load_phone_numbers():
    try:
        with open(PHONE_LIST_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_phone_numbers(numbers):
    with open(PHONE_LIST_FILE, "w") as file:
        json.dump(numbers, file, indent=4)

def checkNumber(number):
    if number is None:
        return 0
    if len(number) == 11 and number.startswith("09") and number.isdigit():
        return 1
    elif len(number) == 13 and number.startswith("+639") and number[1:].isdigit():
        return 2
    return 0

def manage_phone_numbers():
    def add_number():
        new_number = simpledialog.askstring("Add Number", "Enter phone number:")
        check_number = checkNumber(new_number)

        if check_number == 0:
            messagebox.showerror("Invalid Number", "Please enter a valid phone number.")
            return
        elif check_number == 1:
            pass
        elif check_number == 2:
            new_number = new_number[4:]
            new_number = "09" + new_number
        if new_number:  
            phone_numbers.append(new_number)
            update_list()
            save_phone_numbers(phone_numbers)

    def delete_number():
        selected = phone_listbox.curselection()
        if selected:
            phone_numbers.pop(selected[0])
            update_list()
            save_phone_numbers(phone_numbers)

    def rename_number():
        selected = phone_listbox.curselection()
        if selected:
            new_number = simpledialog.askstring("Rename Number", "Enter new phone number:")
            if new_number:
                phone_numbers[selected[0]] = new_number
                update_list()
                save_phone_numbers(phone_numbers)

    def update_list():
        phone_listbox.delete(0, tk.END)
        for num in phone_numbers:
            phone_listbox.insert(tk.END, num)

    phone_numbers = load_phone_numbers()

    phone_window = tk.Toplevel()
    phone_window.title("Manage Phone Numbers")
    phone_window.geometry("300x300")

    phone_listbox = tk.Listbox(phone_window)
    phone_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    update_list()

    tk.Button(phone_window, text="Add", command=add_number).pack(pady=2)
    tk.Button(phone_window, text="Delete", command=delete_number).pack(pady=2)
    tk.Button(phone_window, text="Rename", command=rename_number).pack(pady=2)

import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import pandas as pd
from tkinter import filedialog


PHONE_LIST_FILE = "phone_numbers.json"
PHONE_INFO_FILE = "phone_info.json"

class AddNumberDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Phone number:").grid(row=0, sticky="e")
        tk.Label(master, text="Name:").grid(row=1, sticky="e")

        self.number_entry = tk.Entry(master)
        self.name_entry = tk.Entry(master)

        self.number_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        return self.number_entry

    def apply(self):
        self.result = {
            "number": self.number_entry.get(),
            "name": self.name_entry.get()
        }

class EditNumberDialog(simpledialog.Dialog):
    def __init__(self, parent, number, name, title="Edit Number"):
        self.initial_number = number
        self.initial_name = name
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Phone number:").grid(row=0, sticky="e")
        tk.Label(master, text="Name:").grid(row=1, sticky="e")

        self.number_entry = tk.Entry(master)
        self.name_entry = tk.Entry(master)

        self.number_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        self.number_entry.insert(0, self.initial_number)
        self.name_entry.insert(0, self.initial_name)

        return self.number_entry

    def apply(self):
        self.result = {
            "number": self.number_entry.get(),
            "name": self.name_entry.get()
        }

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

    def import_from_file():
        file_path = filedialog.askopenfilename(
            title="Select CSV or Excel file",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path, dtype=str)
            else:
                df = pd.read_excel(file_path, dtype=str)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")
            return

        name_col_candidates = [col for col in df.columns if "name" in col.lower() and "last" not in col.lower() and "first" in col.lower()]
        name_col = name_col_candidates[0] if name_col_candidates else None

        found_numbers = {}
        
        for idx, row in df.iterrows():
            for col in df.columns:
                val = str(row[col]).strip() if not pd.isna(row[col]) else ""
                check = checkNumber(val)
                if check == 1:
                    number = val
                elif check == 2:
                    number = "+639" + val[2:]
                else:
                    continue

                if number not in found_numbers:
                    name = str(row[name_col]).strip() if name_col and not pd.isna(row[name_col]) else "NO NAME"
                    found_numbers[number] = name

        if not found_numbers:
            messagebox.showinfo("No Valid Numbers", "No valid phone numbers found in the file.")
            return

        phone_numbers.clear()
        phone_info.clear()

        phone_numbers.extend(sorted(found_numbers.keys()))
        for number in phone_numbers:
            phone_info[number] = {"name": found_numbers[number]}

        update_list()
        save_phone_numbers(phone_numbers)
        save_phone_info(phone_info)
        messagebox.showinfo("Import Successful", f"Imported {len(phone_numbers)} phone numbers.")


    def add_number():
        dialog = AddNumberDialog(phone_window, title="Add Number")

        if dialog.result:
            new_number = dialog.result["number"]
            name = dialog.result["name"]

            if not name:
                name = "NO NAME"

            check_number = checkNumber(new_number)

            if check_number == 0:
                messagebox.showerror("Invalid Number", "Please enter a valid phone number.")
                return
            elif check_number == 2:
                new_number = "+639" + new_number[2:]

            if new_number:
                phone_numbers.append(new_number)
                phone_info[new_number] = {"name": name}
                update_list()
                save_phone_numbers(phone_numbers)
                save_phone_info(phone_info)

    def delete_number():
        selected = phone_listbox.curselection()
        if selected:
            phone_numbers.pop(selected[0])
            update_list()
            save_phone_numbers(phone_numbers)
            save_phone_info(phone_info)

    def edit_number():
        selected = phone_listbox.curselection()
        index = selected[0]
        old_number = phone_numbers[index] 
        current_name = phone_info.get(old_number, {}).get("name", "")
        if current_name == "NO NAME":
            current_name = ""
        dialog = EditNumberDialog(phone_window, number=old_number, name=current_name)

        if dialog.result:
            new_number = dialog.result["number"]
            new_name = dialog.result["name"]

            if not new_name:
                new_name = "NO NAME"

            check_number = checkNumber(new_number)

            if check_number == 0:
                messagebox.showerror("Invalid Number", "Please enter a valid phone number.")
                return
            elif check_number == 2:
                new_number = "+639" + new_number[2:]

            if new_number != old_number:
                phone_numbers.remove(old_number)
                phone_numbers.append(new_number)

                phone_info[new_number] = phone_info.pop(old_number)
            
            phone_info[new_number]["name"] = new_name

        update_list()
        save_phone_numbers(phone_numbers)
        save_phone_info(phone_info)

    
    def sort_phone_numbers_by_name():
        def get_name(n):
            name = phone_info.get(n, {}).get("name", "").strip()
            return name if name else "NO NAME"
        
        phone_numbers.sort(key=lambda number: (
            get_name(number).lower() == "no name",
            get_name(number).lower()
        ))


    def update_list():
        sort_phone_numbers_by_name()
        phone_listbox.delete(0, tk.END)
        for num in phone_numbers:
            name = phone_info.get(num, {}).get("name", "").strip() or "NO NAME"
            display_text = f"{name} - ({num})" if name else num
            phone_listbox.insert(tk.END, display_text)


    phone_numbers = load_phone_numbers()

    phone_window = tk.Toplevel()
    phone_window.title("Manage Phone Numbers")
    phone_window.geometry("300x350")

    phone_listbox = tk.Listbox(phone_window)
    phone_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    update_list()

    tk.Button(phone_window, text="Add Number", command=add_number).pack(pady=2)
    tk.Button(phone_window, text="Remove Number", command=delete_number).pack(pady=2)
    tk.Button(phone_window, text="Edit Number", command=edit_number).pack(pady=2)
    tk.Button(phone_window, text="Import From File", command=import_from_file).pack(pady=2)
    tk.Button(phone_window, text="Close", command=phone_window.destroy).pack(pady=2)

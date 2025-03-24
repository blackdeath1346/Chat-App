import tkinter as tk
from tkinter import messagebox, ttk
import json

DATA_FILE = "students.json"

# Load data from JSON file
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"departments": [
            {"code": "CSE", "name": "Computer Science and Engineering"},
            {"code": "ME", "name": "Mechanical Engineering"},
            {"code": "ECE", "name": "Electronics and Communication Engineering"}
        ], "students": []}

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

data = load_data()

# View all students with pagination
def open_view_students_window():
    view_window = tk.Toplevel(root)
    view_window.title("View All Students")
    
    display_frame = tk.Frame(view_window)
    display_frame.pack()
    
    current_page = 0
    records_per_page = 5

    def display_students():
        for widget in display_frame.winfo_children():
            widget.destroy()
        
        start = current_page * records_per_page
        end = start + records_per_page
        students_to_display = data["students"][start:end]
        
        for student in students_to_display:
            dept_name = next((dept["name"] for dept in data["departments"] if dept["code"] == student["dept_code"]), "Unknown")
            tk.Label(display_frame, text=f"{student['roll']} - {student['name']} ({dept_name})").pack()
        
        prev_button.config(state=tk.NORMAL if current_page > 0 else tk.DISABLED)
        next_button.config(state=tk.NORMAL if end < len(data["students"]) else tk.DISABLED)
    
    def next_page():
        nonlocal current_page
        current_page += 1
        display_students()
    
    def prev_page():
        nonlocal current_page
        current_page -= 1
        display_students()
    
    prev_button = tk.Button(view_window, text="Prev", command=prev_page)
    prev_button.pack(side=tk.LEFT)
    next_button = tk.Button(view_window, text="Next", command=next_page)
    next_button.pack(side=tk.RIGHT)
    
    display_students()

# Other student management functions...
def search_student():
    roll = roll_entry.get()
    student = next((s for s in data["students"] if s["roll"] == roll), None)
    if student:
        messagebox.showinfo("Student Found", f"Name: {student['name']}\nDept: {student['dept_code']}\nAddress: {student['address']}\nPhone: {student['phone']}")
    else:
        messagebox.showerror("Error", "Student not found")

def delete_student():
    roll = roll_entry.get()
    global data
    new_students = [s for s in data["students"] if s["roll"] != roll]
    if len(new_students) == len(data["students"]):
        messagebox.showerror("Error", "Student not found")
    else:
        data["students"] = new_students
        save_data(data)
        messagebox.showinfo("Success", "Student deleted successfully")

def add_student():
    add_window = tk.Toplevel(root)
    add_window.title("Add Student")
    tk.Label(add_window, text="Roll:").grid(row=0, column=0)
    roll_entry = tk.Entry(add_window)
    roll_entry.grid(row=0, column=1)
    tk.Label(add_window, text="Name:").grid(row=1, column=0)
    name_entry = tk.Entry(add_window)
    name_entry.grid(row=1, column=1)
    tk.Label(add_window, text="Address:").grid(row=2, column=0)
    address_entry = tk.Entry(add_window)
    address_entry.grid(row=2, column=1)
    tk.Label(add_window, text="Phone:").grid(row=3, column=0)
    phone_entry = tk.Entry(add_window)
    phone_entry.grid(row=3, column=1)
    tk.Label(add_window, text="Department:").grid(row=4, column=0)
    dept_var = tk.StringVar()
    dept_menu = ttk.Combobox(add_window, textvariable=dept_var, values=[d["name"] for d in data["departments"]])
    dept_menu.grid(row=4, column=1)
    
    def save_new_student():
        roll = roll_entry.get()
        if any(s["roll"] == roll for s in data["students"]):
            messagebox.showerror("Error", "Roll number already exists")
            return
        name = name_entry.get()
        address = address_entry.get()
        phone = phone_entry.get()
        dept_name = dept_var.get()
        dept_code = next((d["code"] for d in data["departments"] if d["name"] == dept_name), "")
        if not (roll and name and address and phone and dept_code):
            messagebox.showerror("Error", "All fields are required")
            return
        data["students"].append({"roll": roll, "name": name, "address": address, "phone": phone, "dept_code": dept_code})
        save_data(data)
        messagebox.showinfo("Success", "Student added successfully")
        add_window.destroy()
    
    save_button = tk.Button(add_window, text="Save", command=save_new_student)
    save_button.grid(row=5, column=0, columnspan=2)

# Main window setup
root = tk.Tk()
root.title("Student Management System")

roll_entry = tk.Entry(root)
roll_entry.pack()
search_button = tk.Button(root, text="Search Student", command=search_student)
search_button.pack()
delete_button = tk.Button(root, text="Delete Student", command=delete_student)
delete_button.pack()
add_button = tk.Button(root, text="Add Student", command=add_student)
add_button.pack()
view_all_button = tk.Button(root, text="View All Students", command=open_view_students_window)
view_all_button.pack()

root.mainloop()

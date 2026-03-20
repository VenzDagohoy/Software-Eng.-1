import tkinter as tk
import sqlite3
from tkinter import messagebox, ttk
import hashlib

import dashboard_admin
import dashboard_staff

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect('trash_scheduler.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS staff (
                  username TEXT PRIMARY KEY,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL
                )""")
conn.commit()

def register_user():
    username = username_entry.get()
    password = password_entry.get()
    role = role_var.get()
    
    if not username or not password or not role:
        messagebox.showerror("Error", "Please enter username, password, and role.")
    else:
        cursor.execute("SELECT * FROM staff WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            messagebox.showerror("Error", f"Username '{username}' already exists.")
        else:
            hashed_pwd = hash_password(password)
            cursor.execute("INSERT INTO staff (username, password, role) VALUES (?, ?, ?)", (username, hashed_pwd, role))
            conn.commit()
            messagebox.showinfo("Success", f"User '{username}' registered successfully!")
            toggle_registration_interface()

def login_user():
    username = username_entry.get()
    password = password_entry.get()
    cursor.execute("SELECT * FROM staff WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user and user[1] == hash_password(password):
        messagebox.showinfo("Success", f"Welcome back, {username}!")
        main_window.withdraw()
        if user[2] == 'Admin':
            dashboard_admin.launch_admin_dashboard(main_window)
        elif user[2] == 'Staff':
            dashboard_staff.launch_staff_dashboard(main_window)
    else:
        messagebox.showerror("Error", "Invalid username or password.")

def toggle_registration_interface():
    if registration_button.config('text')[-1] == 'REGISTER':
        registration_button.config(text='LOGIN')
        login_button.config(text='REGISTER', command=register_user)
        main_window.title("Registration Page")
        header_label.config(text="REGISTRATION PAGE")
        role_label.place(x=490, y=400, width=120, height=40)
        role_menu.place(x=610, y=400, width=230, height=40)
    else:
        registration_button.config(text='REGISTER')
        login_button.config(text='LOGIN', command=login_user)
        main_window.title("Login Page")
        header_label.config(text="LOGIN PAGE")
        role_label.place_forget()
        role_menu.place_forget()
    
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    role_var.set('')

main_window = tk.Tk()
main_window.title("TrashTide - Login Page")
main_window.geometry("900x510")
main_window.configure(bg="#d0e0c0")  
main_window.resizable(False, False)

image = tk.PhotoImage(file = "Picture/logo.png") 
tk.Label(main_window, image=image).place(x=50, y=50)

tk.Label(
    main_window,
    text="TrashTide",
    font=("Arial Black", 25, "bold"),
    bg="#4b6f44", 
    fg="white"
).place(x=485, y=60, width=400, height=50)

header_label = tk.Label(
    main_window,
    text="LOGIN PAGE",
    font=("Arial", 14, "bold"),
    bg="#d0e0c0",
    fg="#1c2b1b"  
)
header_label.place(x=600, y=150, width=210, height=35)

label_bg = "#86a87c"  
label_fg = "#1c2b1b"

tk.Label(
    main_window,
    text="Username:",
    font=("Arial", 13, "bold"),
    bg=label_bg,
    fg=label_fg
).place(x=490, y=190, width=120, height=40)

username_entry = tk.Entry(main_window, font=("Arial", 13))
username_entry.place(x=610, y=190, width=230, height=40)

tk.Label(
    main_window,
    text="Password:",
    font=("Arial", 13, "bold"),
    bg=label_bg,
    fg=label_fg
).place(x=490, y=260, width=120, height=40)

password_entry = tk.Entry(main_window, show="*", font=("Arial", 13))
password_entry.place(x=610, y=260, width=230, height=40)

role_label = tk.Label(
    main_window,
    text="Role:",
    font=("Arial", 13, "bold"),
    bg=label_bg,
    fg=label_fg
)
role_var = tk.StringVar()
role_menu = ttk.Combobox(main_window, textvariable=role_var, state="readonly", font=("Arial", 13, "bold"))
role_menu['values'] = ('Admin', 'Staff')

button_bg_login = "#2e8b57"     
button_bg_register = "#3b5998"  
button_fg = "white"

login_button = tk.Button(
    main_window,
    text="LOGIN",
    command=login_user,
    font=("Arial", 15),
    bg=button_bg_login,
    fg=button_fg,
    activebackground="#3cb371"
)
login_button.place(x=610, y=310, width=130, height=30)

registration_button = tk.Button(
    main_window,
    text="REGISTER",
    command=toggle_registration_interface,
    font=("Arial", 15),
    bg=button_bg_register,
    fg="white",
    activebackground="#5f9ea0"
)
registration_button.place(x=610, y=350, width=130, height=30)

main_window.mainloop()
conn.close()
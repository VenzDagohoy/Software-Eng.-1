import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

def launch_admin_dashboard(main_window):
    conn = sqlite3.connect("trash_scheduler.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        waste_type TEXT,
        collection_date TEXT,
        collection_time TEXT,
        assigned_staff TEXT,
        status TEXT
    )""")
    conn.commit()

    admin = tk.Toplevel(main_window)
    admin.title("TrashTide - Admin Dashboard")
    admin.geometry("1000x600")
    admin.configure(bg="#121417")
    admin.resizable(False, False)

    font_style = ("Arial", 12, "bold")
    entry_style = {"font": font_style, "bg": "#fff"}

    def label_entry(text, x, y):
        tk.Label(admin, text=text, bg="#121417", fg="white", font=font_style).place(x=x, y=y)
        entry = tk.Entry(admin, **entry_style)
        entry.place(x=x+120, y=y, width=200, height=30)
        return entry

    location_entry = label_entry("Location:", 40, 70)
    waste_entry = label_entry("Waste Type:", 400, 70)
    date_entry = label_entry("Date:", 40, 120)
    time_entry = label_entry("Time:", 400, 120)
    staff_entry = label_entry("Staff:", 40, 170)

    tree_frame = tk.Frame(admin, bg="#1a1a1a")
    tree_frame.place(x=20, y=280, width=960, height=300)

    tree = ttk.Treeview(tree_frame, columns=("ID", "Location", "Waste", "Date", "Time", "Staff", "Status"), show="headings")
    tree.heading("ID", text="ID")
    tree.column("ID", width=50)
    for col in ("Location", "Waste", "Date", "Time", "Staff", "Status"):
        tree.heading(col, text=col)
        tree.column(col, width=140)
    tree.pack(fill="both", expand=True)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#1a1a1a", foreground="white", rowheight=25, fieldbackground="#1a1a1a")
    style.configure("Treeview.Heading", background="#1a1a1a", foreground="white", font=("Arial", 11, "bold"))

    def validate_date(date_str):
        try:
            datetime.strptime(date_str.strip(), "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def load_data():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT id, location, waste_type, collection_date, collection_time, assigned_staff, status FROM schedules ORDER BY collection_date, collection_time")
        for row in cursor.fetchall():
            row = list(row)
            try:
                row[4] = datetime.strptime(row[4], "%H:%M").strftime("%I:%M %p") 
            except:
                pass
            tree.insert("", "end", values=row)

    def clear_entries():
        for entry in [location_entry, waste_entry, date_entry, time_entry, staff_entry]:
            entry.delete(0, tk.END)

    def add_schedule():
        time_input = time_entry.get().strip()
        try:
            time_24hr = datetime.strptime(time_input, "%I:%M %p").strftime("%H:%M")
        except ValueError:
            messagebox.showerror("Invalid Time", "Time must be in HH:MM AM/PM format (e.g., 02:30 PM).")
            return

        if not validate_date(date_entry.get()):
            messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format (e.g., 2003-12-25).")
            return

        values = (
            location_entry.get(),
            waste_entry.get(),
            date_entry.get(),
            time_24hr,
            staff_entry.get(),
            "Pending"
        )

        if any(v.strip() == "" for v in values[:-1]):
            messagebox.showerror("Error", "All fields are required.")
            return

        cursor.execute("""
            INSERT INTO schedules (location, waste_type, collection_date, collection_time, assigned_staff, status)
            VALUES (?, ?, ?, ?, ?, ?)""", values)
        conn.commit()
        load_data()
        clear_entries()

    def delete_schedule():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Entry", "Please select a schedule to delete.")
            return
        item = tree.item(selected)
        schedule_id = item["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this schedule?")
        if confirm:
            cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
            conn.commit()
            load_data()
            clear_entries()

    def close_and_logout():
        admin.destroy()
        main_window.deiconify()

    tk.Label(admin, text="TrashTide Admin Panel", bg="#121417", fg="#89CFF0", font=("Arial", 20, "bold")).place(x=350, y=10)

    button_style = {"font": ("Arial", 11, "bold"), "bg": "#121417", "fg": "#89CFF0", "activebackground": "#1e1e1e", "activeforeground": "#89CFF0"}
    tk.Button(admin, text="Add Schedule", command=add_schedule, **button_style).place(x=750, y=50, width=130, height=30)
    tk.Button(admin, text="Clear", command=clear_entries, **button_style).place(x=750, y=90, width=130, height=30)
    tk.Button(admin, text="Delete", command=delete_schedule, **button_style).place(x=750, y=130, width=130, height=30)
    tk.Button(admin, text="Log Out", command=close_and_logout, **button_style).place(x=750, y=170, width=130, height=30)

    load_data()
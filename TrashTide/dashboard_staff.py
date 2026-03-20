import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

def launch_staff_dashboard(main_window):
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

    staff = tk.Toplevel(main_window)
    staff.title("TrashTide - Staff Dashboard")
    staff.geometry("1000x600")
    staff.configure(bg="#121417")
    staff.resizable(False, False)

    font_style = ("Arial", 12, "bold")

    tk.Label(staff, text="TrashTide Staff Panel", bg="#121417", fg="#89CFF0", font=("Arial", 20, "bold")).place(x=350, y=10)

    # Input fields
    tk.Label(staff, text="Assigned Staff:", bg="#121417", fg="white", font=font_style).place(x=40, y=70)
    staff_name_var = tk.StringVar()
    tk.Entry(staff, textvariable=staff_name_var, font=font_style).place(x=165, y=70, width=200, height=30)

    tk.Label(staff, text="Year (YYYY):", bg="#121417", fg="white", font=font_style).place(x=385, y=70)
    year_var = tk.StringVar()
    tk.Entry(staff, textvariable=year_var, font=font_style).place(x=490, y=70, width=100, height=30)

    tk.Label(staff, text="Month (MM):", bg="#121417", fg="white", font=font_style).place(x=615, y=70)
    month_var = tk.StringVar()
    tk.Entry(staff, textvariable=month_var, font=font_style).place(x=720, y=70, width=60, height=30)

    tk.Label(staff, text="Day (DD):", bg="#121417", fg="white", font=font_style).place(x=795, y=70)
    day_var = tk.StringVar()
    tk.Entry(staff, textvariable=day_var, font=font_style).place(x=880, y=70, width=60, height=30)

    # Treeview
    tree_frame = tk.Frame(staff, bg="#1a1a1a")
    tree_frame.place(x=20, y=180, width=960, height=380)

    tree = ttk.Treeview(tree_frame, columns=("Location", "Waste", "Date", "Time", "Staff", "Status"), show="headings")
    for col in ("Location", "Waste", "Date", "Time", "Staff", "Status"):
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#1a1a1a", foreground="white", rowheight=25, fieldbackground="#1a1a1a")
    style.configure("Treeview.Heading", background="#1a1a1a", foreground="white", font=("Arial", 11, "bold"))

    def load_assignments():
        staff_name = staff_name_var.get().strip()
        year = year_var.get().strip()
        month = month_var.get().strip()
        day = day_var.get().strip()

        query = """
        SELECT location, waste_type, collection_date, collection_time, assigned_staff, status
        FROM schedules
        WHERE 1 = 1
        """
        params = []

        if staff_name:
            query += " AND assigned_staff = ?"
            params.append(staff_name)

        if year:
            query += " AND strftime('%Y', collection_date) = ?"
            params.append(year)

        if month:
            query += " AND strftime('%m', collection_date) = ?"
            params.append(month.zfill(2))

        if day:
            query += " AND strftime('%d', collection_date) = ?"
            params.append(day.zfill(2))

        query += " ORDER BY collection_date, collection_time"

        for row in tree.get_children():
            tree.delete(row)

        cursor.execute(query, params)
        for row in cursor.fetchall():
            row = list(row)
            try:
                row[3] = datetime.strptime(row[3], "%H:%M").strftime("%I:%M %p")
            except:
                pass
            tree.insert("", "end", values=row)

    def mark_completed():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Entry", "Please select a schedule to mark as Completed.")
            return
        item = tree.item(selected)
        location, waste_type, collection_date, collection_time, staff_name, status = item["values"]
        if status == "Completed":
            messagebox.showinfo("Already Completed", "This schedule is already marked as Completed.")
            return
        try:
            time_24hr = datetime.strptime(collection_time.strip(), "%I:%M %p").strftime("%H:%M")
        except:
            messagebox.showerror("Time Format Error", "Could not parse time. Ensure it is in AM/PM format.")
            return
        cursor.execute("""
            UPDATE schedules SET status = 'Completed'
            WHERE location = ? AND waste_type = ? AND collection_date = ? AND collection_time = ? AND assigned_staff = ?
        """, (location, waste_type, collection_date, time_24hr, staff_name))
        conn.commit()
        load_assignments()

    def logout():
        staff.destroy()
        main_window.deiconify()

    button_style = {"font": font_style, "bg": "#121417", "fg": "#89CFF0", "activebackground": "#1e1e1e", "activeforeground": "#89CFF0"}
    tk.Button(staff, text="Load Schedules", command=load_assignments, **button_style).place(x=40, y=110, width=160, height=30)
    tk.Button(staff, text="Mark as Completed", command=mark_completed, **button_style).place(x=210, y=110, width=180, height=30)
    tk.Button(staff, text="Log Out", command=logout, **button_style).place(x=400, y=110, width=100, height=30)
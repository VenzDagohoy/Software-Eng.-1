import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

def launch_admin_dashboard(main_window):
    conn = sqlite3.connect("techsync.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room TEXT,
        issue_category TEXT,
        date_reported TEXT,
        time_reported TEXT,
        assigned_tech TEXT,
        status TEXT
    )""")
    conn.commit()

    admin = tk.Toplevel(main_window)
    admin.title("TechSync - Admin Dashboard")
    admin.geometry("1000x600")
    admin.configure(bg="#121417")
    admin.resizable(False, False)

    font_style = ("Arial", 12, "bold")
    entry_style = {"font": font_style, "bg": "#fff"}

    def label_entry(text, x, y):
        tk.Label(admin, text=text, bg="#121417", fg="white", font=font_style).place(x=x, y=y)
        entry = tk.Entry(admin, **entry_style)
        entry.place(x=x+130, y=y, width=200, height=30)
        return entry

    room_entry = label_entry("Room/Dept:", 40, 70)
    issue_entry = label_entry("Issue Category:", 380, 70)
    date_entry = label_entry("Date:", 40, 120)
    time_entry = label_entry("Time:", 380, 120)
    tech_entry = label_entry("Assigned Tech:", 40, 170)

    tree_frame = tk.Frame(admin, bg="#1a1a1a")
    tree_frame.place(x=20, y=280, width=960, height=300)

    tree = ttk.Treeview(tree_frame, columns=("Ticket ID", "Room", "Issue", "Date", "Time", "Technician", "Status"), show="headings")
    tree.heading("Ticket ID", text="Ticket ID")
    tree.column("Ticket ID", width=70)
    for col in ("Room", "Issue", "Date", "Time", "Technician", "Status"):
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
        cursor.execute("SELECT id, room, issue_category, date_reported, time_reported, assigned_tech, status FROM tickets ORDER BY date_reported, time_reported")
        for row in cursor.fetchall():
            row = list(row)
            try:
                row[4] = datetime.strptime(row[4], "%H:%M").strftime("%I:%M %p") 
            except:
                pass
            tree.insert("", "end", values=row)

    def clear_entries():
        for entry in [room_entry, issue_entry, date_entry, time_entry, tech_entry]:
            entry.delete(0, tk.END)

    def add_ticket():
        time_input = time_entry.get().strip()
        try:
            time_24hr = datetime.strptime(time_input, "%I:%M %p").strftime("%H:%M")
        except ValueError:
            messagebox.showerror("Invalid Time", "Time must be in HH:MM AM/PM format (e.g., 02:30 PM).")
            return

        if not validate_date(date_entry.get()):
            messagebox.showerror("Invalid Date", "Date must be in YYYY-MM-DD format (e.g., 2026-12-25).")
            return

        values = (
            room_entry.get(),
            issue_entry.get(),
            date_entry.get(),
            time_24hr,
            tech_entry.get(),
            "Pending"
        )

        if any(v.strip() == "" for v in values[:-1]):
            messagebox.showerror("Error", "All fields are required.")
            return

        cursor.execute("""
            INSERT INTO tickets (room, issue_category, date_reported, time_reported, assigned_tech, status)
            VALUES (?, ?, ?, ?, ?, ?)""", values)
        conn.commit()
        load_data()
        clear_entries()

    def delete_ticket():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Select Entry", "Please select a ticket to delete.")
            return
        item = tree.item(selected)
        ticket_id = item["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this ticket?")
        if confirm:
            cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            conn.commit()
            load_data()
            clear_entries()

    def close_and_logout():
        admin.destroy()
        main_window.deiconify()

    tk.Label(admin, text="TechSync Admin Panel", bg="#121417", fg="#89CFF0", font=("Arial", 20, "bold")).place(x=350, y=10)

    button_style = {"font": ("Arial", 11, "bold"), "bg": "#121417", "fg": "#89CFF0", "activebackground": "#1e1e1e", "activeforeground": "#89CFF0"}
    tk.Button(admin, text="Create Ticket", command=add_ticket, **button_style).place(x=765, y=50, width=130, height=30)
    tk.Button(admin, text="Clear", command=clear_entries, **button_style).place(x=765, y=90, width=130, height=30)
    tk.Button(admin, text="Delete Ticket", command=delete_ticket, **button_style).place(x=765, y=130, width=130, height=30)
    tk.Button(admin, text="Log Out", command=close_and_logout, **button_style).place(x=765, y=170, width=130, height=30)

    load_data()
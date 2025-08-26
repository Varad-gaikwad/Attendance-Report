import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="varad",
    database="attendance"
)
cursor = conn.cursor()

# --- Database Setup ---
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS subjects (
    subject_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    student_id INTEGER,
    subject_name TEXT NOT NULL,
    total_classes INTEGER DEFAULT 0,
    attended INTEGER DEFAULT 0,
    FOREIGN KEY(student_id) REFERENCES students(student_id)
)
""")
conn.commit()


# --- Core Functions ---
def add_student():
    name = simpledialog.askstring("Add Student", "Enter student name:")
    if name:
        cursor.execute("INSERT INTO students (name) VALUES (%s)", (name,))
        conn.commit()
        messagebox.showinfo("Success", f"Student '{name}' added!")

def add_subject():
    student_id = simpledialog.askinteger("Add Subject", "Enter student ID:")
    subject = simpledialog.askstring("Add Subject", "Enter subject name:")
    if student_id and subject:
        cursor.execute("INSERT INTO subjects (student_id, subject_name) VALUES (%s,%s)", (student_id, subject))
        conn.commit()
        messagebox.showinfo("Success", f"Subject '{subject}' added for Student {student_id}")

def mark_attendance():
    student_id = simpledialog.askinteger("Mark Attendance", "Enter student ID:")
    subject = simpledialog.askstring("Mark Attendance", "Enter subject name:")
    status = simpledialog.askstring("Mark Attendance", "Present? (y/n):")
    if student_id and subject:
        if status and status.lower() == "y":
            cursor.execute("""
                UPDATE subjects 
                SET total_classes = total_classes + 1, attended = attended + 1
                WHERE student_id = %s AND subject_name = %s
            """, (student_id, subject))
        else:
            cursor.execute("""
                UPDATE subjects 
                SET total_classes = total_classes + 1
                WHERE student_id = %s AND subject_name = %s
            """, (student_id, subject))
        conn.commit()
        messagebox.showinfo("Success", f"Attendance marked for {subject} (Student {student_id})")

def view_report():
    student_id = simpledialog.askinteger("View Report", "Enter student ID:")
    if student_id:
        cursor.execute("SELECT subject_name, attended, total_classes FROM subjects WHERE student_id = %s", (student_id,))
        records = cursor.fetchall()
        
        report_win = tk.Toplevel(root)
        report_win.title("Attendance Report")
        text_area = scrolledtext.ScrolledText(report_win, width=50, height=15)
        text_area.pack(padx=10, pady=10)

        text_area.insert(tk.END, "Attendance Report:\n")
        for subject, attended, total in records:
            percent = (attended / total) * 100 if total > 0 else 0
            text_area.insert(tk.END, f" - {subject}: {attended}/{total} ({percent:.2f}%)\n")

def predict_safe_absences():
    student_id = simpledialog.askinteger("Predict Absences", "Enter student ID:")
    subject = simpledialog.askstring("Predict Absences", "Enter subject name:")
    if student_id and subject:
        cursor.execute("SELECT attended, total_classes FROM subjects WHERE student_id = %s AND subject_name = %s", 
                       (student_id, subject))
        record = cursor.fetchone()
        if record:
            attended, total = record
            if total == 0:
                messagebox.showwarning("Info", "Not enough data for prediction.")
                return

            safe_absences = 0
            while (attended / (total + safe_absences + 1)) * 100 >= 75:
                safe_absences += 1

            messagebox.showinfo("Prediction", f"You can safely miss {safe_absences} more classes in {subject} (while staying above 75%).")
        else:
            messagebox.showerror("Error", "Subject not found.")


# --- Tkinter GUI ---
root = tk.Tk()
root.title("Digital Peer Attendance Manager")
root.geometry("400x400")

label = tk.Label(root, text="Digital Peer Attendance Manager", font=("Arial", 14, "bold"))
label.pack(pady=15)

tk.Button(root, text="Add Student", width=25, command=add_student).pack(pady=5)
tk.Button(root, text="Add Subject", width=25, command=add_subject).pack(pady=5)
tk.Button(root, text="Mark Attendance", width=25, command=mark_attendance).pack(pady=5)
tk.Button(root, text="View Attendance Report", width=25, command=view_report).pack(pady=5)
tk.Button(root, text="Predict Safe Absences", width=25, command=predict_safe_absences).pack(pady=5)
tk.Button(root, text="Exit", width=25, command=root.quit).pack(pady=20)

root.mainloop()

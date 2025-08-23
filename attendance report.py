import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="varad",
    database="attendance"
)


cursor = conn.cursor()

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


def add_student(name):
    cursor.execute("INSERT INTO students (name) VALUES (%s)", (name,))
    conn.commit()
    print(" Student",name,"added!")


def add_subject(student_id, subject_name):
    cursor.execute("INSERT INTO subjects (student_id, subject_name) VALUES (%s,%s)", (student_id, subject_name))
    conn.commit()
    print("Subject",subject_name,"added for Student",student_id,"!")


def mark_attendance(student_id, subject_name, present=True):
    if present:
        cursor.execute("""
            UPDATE subjects 
            SET total_classes = total_classes + 1, attended = attended + 1
            WHERE student_id = %s AND subject_name = %s
        """, (student_id, subject_name))
    else:
        cursor.execute("""
            UPDATE subjects 
            SET total_classes = total_classes + 1
            WHERE student_id = %s AND subject_name = %s
        """, (student_id, subject_name))
    conn.commit()
    print("Attendance marked for",subject_name,student_id,"!")


def view_report(student_id):
    cursor.execute("SELECT subject_name, attended, total_classes FROM subjects WHERE student_id = %s", (student_id,))
    records = cursor.fetchall()
    
    print("Attendance Report:")
    for subject, attended, total in records:
        if total == 0:
            percent = 0
        else:
            percent = (attended / total) * 100
        print(f" - {subject}: {attended}/{total} ({percent:.2f}%)")
    print("")


def predict_safe_absences(student_id, subject_name, min_percent=75):
    cursor.execute("SELECT attended, total_classes FROM subjects WHERE student_id = %s AND subject_name = %s", 
                   (student_id, subject_name))
    record = cursor.fetchone()
    if record:
        attended, total = record
        if total == 0:
            print(" Not enough data for prediction.")
            return
        
        # Formula: (attended / (total + x)) * 100 >= min_percent
        safe_absences = 0
        while (attended / (total + safe_absences + 1)) * 100 >= min_percent:
            safe_absences += 1
        
        print("You can safely miss",safe_absences," more classes in",subject_name,"and stay above",min_percent,"%.")
    else:
        print("Subject not found.")


def main():
    while True:
        print("\n===== Digital Peer Attendance Manager =====")
        print("1. Add Student")
        print("2. Add Subject")
        print("3. Mark Attendance")
        print("4. View Attendance Report")
        print("5. Predict Safe Absences")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Enter student name: ")
            add_student(name)

        elif choice == "2":
            student_id = int(input("Enter student ID: "))
            subject = input("Enter subject name: ")
            add_subject(student_id, subject)

        elif choice == "3":
            student_id = int(input("Enter student ID: "))
            subject = input("Enter subject name: ")
            status = input("Present? (y/n): ").lower()
            mark_attendance(student_id, subject, present=(status == "y"))

        elif choice == "4":
            student_id = int(input("Enter student ID: "))
            view_report(student_id)

        elif choice == "5":
            student_id = int(input("Enter student ID: "))
            subject = input("Enter subject name: ")
            predict_safe_absences(student_id, subject)

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()

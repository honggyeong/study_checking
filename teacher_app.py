import flet as ft
import sqlite3
from datetime import datetime

DB_NAME = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_students():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, name FROM students')
    students = c.fetchall()
    conn.close()
    return students

def add_student(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO students (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def mark_attendance(student_id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', (student_id, today, status))
    conn.commit()
    conn.close()

def get_attendance():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''
        SELECT s.name, a.status FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.date = ?
    ''', (today,))
    records = c.fetchall()
    conn.close()
    return records

def main(page: ft.Page):
    page.title = "선생님용 출석 관리"
    init_db()

    name_field = ft.TextField(label="학생 이름 입력")
    add_btn = ft.ElevatedButton("학생 추가", on_click=lambda e: (add_student(name_field.value), page.update(), name_field.update()))

    def refresh_attendance(e=None):
        records = get_attendance()
        attendance_list.controls.clear()
        for name, status in records:
            attendance_list.controls.append(ft.Text(f"{name}: {status}"))
        page.update()

    attendance_list = ft.Column()
    refresh_btn = ft.ElevatedButton("출석 현황 새로고침", on_click=refresh_attendance)

    def add_student_event(e):
        add_student(name_field.value)
        name_field.value = ""
        page.update()

    add_btn.on_click = add_student_event

    page.add(
        ft.Row([name_field, add_btn]),
        refresh_btn,
        attendance_list
    )
    refresh_attendance()

if __name__ == "__main__":
    ft.app(target=main) 
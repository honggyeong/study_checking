import flet as ft
import sqlite3
from datetime import datetime

DB_NAME = "attendance.db"

def get_students():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, name FROM students')
    students = c.fetchall()
    conn.close()
    return students

def mark_attendance(student_id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', (student_id, today, status))
    conn.commit()
    conn.close()

def get_my_attendance(student_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT date, status FROM attendance WHERE student_id = ? ORDER BY date DESC LIMIT 5', (student_id,))
    records = c.fetchall()
    conn.close()
    return records

def main(page: ft.Page):
    page.title = "학생용 출석 체크"
    students = get_students()
    student_names = [name for _, name in students]
    student_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(name) for name in student_names],
        label="이름 선택"
    )
    status_text = ft.Text("")
    attendance_list = ft.Column()

    def check_attendance(e):
        selected_name = student_dropdown.value
        if not selected_name:
            status_text.value = "이름을 선택하세요."
            page.update()
            return
        student_id = None
        for sid, name in students:
            if name == selected_name:
                student_id = sid
                break
        if student_id:
            mark_attendance(student_id, "출석")
            status_text.value = f"{selected_name}님, 출석이 완료되었습니다."
            refresh_attendance()
        else:
            status_text.value = "학생 정보를 찾을 수 없습니다."
        page.update()

    def refresh_attendance():
        selected_name = student_dropdown.value
        if not selected_name:
            attendance_list.controls.clear()
            page.update()
            return
        student_id = None
        for sid, name in students:
            if name == selected_name:
                student_id = sid
                break
        if student_id:
            records = get_my_attendance(student_id)
            attendance_list.controls.clear()
            for date, status in records:
                attendance_list.controls.append(ft.Text(f"{date}: {status}"))
        page.update()

    check_btn = ft.ElevatedButton("출석 체크", on_click=check_attendance)
    student_dropdown.on_change = lambda e: refresh_attendance()

    page.add(
        student_dropdown,
        check_btn,
        status_text,
        ft.Text("최근 출석 기록:"),
        attendance_list
    )

if __name__ == "__main__":
    ft.app(target=main) 
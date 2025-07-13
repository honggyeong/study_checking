import flet as ft
import pyrebase
from firebase_config import firebaseConfig
from datetime import datetime

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

def get_students():
    try:
        students = db.child("students").get()
        return [(s.key(), s.val()["name"]) for s in students.each()] if students.each() else []
    except Exception as e:
        # 데이터가 없거나 404일 때 빈 리스트 반환
        return []

def mark_attendance(student_id, status):
    today = datetime.now().strftime('%Y-%m-%d')
    db.child("attendance").child(today).child(student_id).set({"status": status})

def get_my_attendance(student_id):
    try:
        records = []
        attendance_days = db.child("attendance").get()
        if attendance_days.each():
            for day in attendance_days.each():
                date = day.key()
                if student_id in day.val():
                    status = day.val()[student_id]["status"]
                    records.append((date, status))
        return sorted(records, reverse=True)[:5]
    except Exception as e:
        # 데이터가 없거나 404일 때 빈 리스트 반환
        return []

def main(page: ft.Page):
    page.title = "학생용 출석 체크 (Firebase)"
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
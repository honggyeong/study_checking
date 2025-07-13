import flet as ft
import pyrebase
from firebase_config import firebaseConfig
from datetime import datetime

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

def add_student(name):
    # 학생 이름을 students에 추가
    db.child("students").push({"name": name})

def get_students():
    students = db.child("students").get()
    return [(s.key(), s.val()["name"]) for s in students.each()] if students.each() else []

def mark_attendance(student_id, status):
    today = datetime.now().strftime('%Y-%m-%d')
    db.child("attendance").child(today).child(student_id).set({"status": status})

def get_attendance():
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        records = db.child("attendance").child(today).get()
        result = []
        if records.each():
            for r in records.each():
                student_id = r.key()
                status = r.val()["status"]
                name = db.child("students").child(student_id).get().val()["name"]
                result.append((name, status))
        return result
    except Exception as e:
        # 데이터가 없거나 404일 때 빈 리스트 반환
        return []

def main(page: ft.Page):
    page.title = "선생님용 출석 관리 (Firebase)"
    name_field = ft.TextField(label="학생 이름 입력")
    add_btn = ft.ElevatedButton("학생 추가")
    attendance_list = ft.Column()
    refresh_btn = ft.ElevatedButton("출석 현황 새로고침")

    def add_student_event(e):
        if name_field.value.strip():
            add_student(name_field.value.strip())
            name_field.value = ""
            page.snack_bar = ft.SnackBar(ft.Text("학생이 추가되었습니다."))
            page.snack_bar.open = True
            page.update()

    def refresh_attendance(e=None):
        attendance_list.controls.clear()
        for name, status in get_attendance():
            attendance_list.controls.append(ft.Text(f"{name}: {status}"))
        page.update()

    add_btn.on_click = add_student_event
    refresh_btn.on_click = refresh_attendance

    page.add(
        ft.Row([name_field, add_btn]),
        refresh_btn,
        attendance_list
    )
    refresh_attendance()

if __name__ == "__main__":
    ft.app(target=main) 
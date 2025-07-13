import asyncio
from bleak import BleakScanner
import pyrebase
from firebase_config import firebaseConfig
from datetime import datetime

# 파이어베이스 초기화
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# 미리 등록된 학생 BLE MAC 주소와 이름 매핑 (예시)
student_ble = {
    "AA:BB:CC:DD:EE:FF": "홍길동",
    "11:22:33:44:55:66": "김철수",
    # 여기에 학생 BLE MAC 주소와 이름을 추가하세요
}

async def scan_ble():
    print("BLE 출석 체크를 시작합니다. (10초간 스캔)")
    devices = await BleakScanner.discover(timeout=10.0)
    found = set()
    for d in devices:
        if d.address in student_ble:
            name = student_ble[d.address]
            today = datetime.now().strftime('%Y-%m-%d')
            db.child("attendance").child(today).child(d.address).set({"name": name, "status": "출석"})
            print(f"{name}({d.address}) 출석 완료!")
            found.add(d.address)
    if not found:
        print("등록된 학생의 BLE 신호를 찾지 못했습니다.")

if __name__ == "__main__":
    asyncio.run(scan_ble()) 
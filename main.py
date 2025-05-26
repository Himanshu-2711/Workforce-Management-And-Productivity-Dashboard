from tracker.login_tracker import login, handle_exit
from tracker.activity_tracker import ActivityTracker
from tracker.location_detector import detect_location
from config import EMPLOYEE_ID
import signal
import atexit
from datetime import datetime
import json
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print("✅ Connected to Socket.IO server")

@sio.event
def disconnect():
    print("❌ Disconnected from Socket.IO server")

def send_location():
    location = detect_location()
    location_data = {
        "employeeId": EMPLOYEE_ID,
        "status": "Location Update",
        "location": location,
        "timestamp": datetime.now().isoformat()
    }
    sio.emit("statusUpdate", location_data)
    print(f"[LOCATION] Sent location: {location}")

def handle_shutdown():
    handle_exit(sio)
    sio.disconnect()

if __name__ == "__main__":
    try:
        sio.connect("http://localhost:5000")
        atexit.register(handle_shutdown)

        login(sio)
        send_location()

        tracker = ActivityTracker(sio)
        tracker.start()

        while True:
            pass  # keep script alive

    except KeyboardInterrupt:
        handle_shutdown()
    except Exception as e:
        print(f"[ERROR] {e}")

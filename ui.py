import tkinter as tk
from tkinter import messagebox, PhotoImage
from tracker.login_tracker import login, handle_exit
from tracker.activity_tracker import ActivityTracker
from tracker.location_detector import detect_location
from config import EMPLOYEE_ID
import socketio
from datetime import datetime
import requests

# Socket.IO setup
sio = socketio.Client()

@sio.event
def connect():
    print("✅ Connected to Socket.IO server")

@sio.event
def disconnect():
    print("❌ Disconnected from Socket.IO server")

tracker = None

# Dashboard Window
class EmployeeDashboard(tk.Toplevel):
    def __init__(self, parent_app, emp_id, login_time):
        super().__init__()
        self.parent_app = parent_app
        self.emp_id = emp_id
        self.login_time = login_time
        self.title("Employee Dashboard")
        self.geometry("1000x600")
        self.configure(bg="#f9f9f9")

        # Clock label in top right
        self.clock_label = tk.Label(self, font=("Segoe UI", 11), bg="#f9f9f9", fg="black")
        self.clock_label.place(relx=1.0, y=10, x=-20, anchor="ne")
        self.update_clock()

        tk.Label(self, text=f"Welcome, Christopher", font=("Segoe UI", 16, "bold"), bg="#f9f9f9").pack(pady=20)

        # Status row
        status_row = tk.Frame(self, bg="#f9f9f9")
        tk.Label(status_row, text="Status:", font=("Segoe UI", 12, "bold"), width=25, anchor='w', bg="#f9f9f9").pack(side=tk.LEFT)
        tk.Label(status_row, text="Login", font=("Segoe UI", 12, "bold"), fg="green", bg="#f9f9f9").pack(side=tk.LEFT)
        status_row.pack(pady=5, padx=30, anchor="w")

        # IP
        try:
            ip_address = requests.get("https://api.ipify.org").text
        except:
            ip_address = "Unavailable"

        # Details
        details = {
            "Employee ID": emp_id,
            "Name": "Christopher Roberts",
            "Email": "Christopher.Roberts@example.com",
            "Joining Date": "2022-01-15",
            "Attendance": "95%",
            "Working Hours (This Week)": "36 hrs",
            "IP Address": ip_address,
            "Work Mode": "Office",
            "Login Time": login_time,
            "Feedback from Senior": "Keep up the good work!"
        }

        for key, value in details.items():
            row = tk.Frame(self, bg="#f9f9f9")
            tk.Label(row, text=f"{key}:", font=("Segoe UI", 12), width=25, anchor='w', bg="#f9f9f9").pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Segoe UI", 12), fg="blue", anchor='w', bg="#f9f9f9").pack(side=tk.LEFT)
            row.pack(pady=5, padx=30, anchor="w")

        tk.Button(self, text="Logout", command=self.handle_logout,
                  font=("Segoe UI", 12, "bold"), bg="red", fg="white").pack(pady=30)

    def update_clock(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def handle_logout(self):
        confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?")
        if not confirm:
            return
        handle_exit(sio)
        if tracker:
            tracker.running = False
        if sio.connected:
            sio.disconnect()
        print(f"[LOGOUT] {self.emp_id} logged out")

        self.destroy()
        self.parent_app.logged_in = False
        if self.parent_app.status_label.winfo_exists():
            self.parent_app.status_label.config(text="Status: Logged Out", fg="red")
        if self.parent_app.login_btn.winfo_exists():
            self.parent_app.login_btn.config(text="Login", state="normal")
        self.parent_app.root.deiconify()

# Main App
class WorkforceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Login Panel")
        self.root.state("zoomed")
        self.logged_in = False
        self.root.configure(bg="#f2f2f2")

        self.frame = tk.Frame(root, bg="#f2f2f2")
        self.frame.pack(pady=50)

        try:
            self.logo = PhotoImage(file="./Inspirisys-logo.png")
            tk.Label(self.frame, image=self.logo, bg="#f2f2f2").pack(pady=10)
        except:
            pass

        tk.Label(self.frame, text="Workforce Tracker", font=("Segoe UI", 24, "bold"), bg="#f2f2f2", fg="#333").pack(pady=(0, 30))

        tk.Label(self.frame, text="Employee ID", bg="#f2f2f2", font=("Segoe UI", 12)).pack()
        self.emp_id_entry = tk.Entry(self.frame, font=("Segoe UI", 12))
        self.emp_id_entry.insert(0, EMPLOYEE_ID)
        self.emp_id_entry.pack(pady=5)

        tk.Label(self.frame, text="Password", bg="#f2f2f2", font=("Segoe UI", 12)).pack()
        self.password_entry = tk.Entry(self.frame, show="*", font=("Segoe UI", 12))
        self.password_entry.pack(pady=5)

        self.login_btn = tk.Button(self.frame, text="Login", command=self.toggle_login,
                                   font=("Segoe UI", 12, "bold"), bg="#007bff", fg="white", width=20)
        self.login_btn.pack(pady=15)

        self.status_label = tk.Label(self.frame, text="Status: Logged Out", bg="#f2f2f2", fg="red", font=("Segoe UI", 11, "italic"))
        self.status_label.pack(pady=5)

        self.link_frame = tk.Frame(self.frame, bg="#f2f2f2")
        self.link_frame.pack(pady=(20, 0))
        tk.Button(self.link_frame, text="Sign Up", font=("Segoe UI", 10),
                  fg="#007bff", bg="#f2f2f2", bd=0, command=self.show_signup).grid(row=0, column=0, padx=10)
        tk.Button(self.link_frame, text="Forgot Password?", font=("Segoe UI", 10),
                  fg="#007bff", bg="#f2f2f2", bd=0, command=self.show_forgot).grid(row=0, column=1, padx=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def toggle_login(self):
        global tracker
        if not self.logged_in:
            emp_id = self.emp_id_entry.get()
            password = self.password_entry.get()

            if password != "1234":
                messagebox.showerror("Error", "Invalid password")
                return

            try:
                sio.connect("http://localhost:5000")
                login(sio)
                self.send_location(emp_id)
                tracker = ActivityTracker(sio)
                tracker.start()

                login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.logged_in = True
                self.status_label.config(text=f"Status: Logged In as {emp_id}", fg="green")
                self.login_btn.config(text="Logout")
                self.root.withdraw()
                EmployeeDashboard(self, emp_id, login_time)

            except Exception as e:
                messagebox.showerror("Connection Error", str(e))
        else:
            self.logout()

    def send_location(self, emp_id):
        location = detect_location()
        location_data = {
            "employeeId": emp_id,
            "status": "Location Update",
            "location": location,
            "timestamp": datetime.now().isoformat()
        }
        sio.emit("statusUpdate", location_data)
        print(f"[LOCATION] Sent: {location}")

    def logout(self):
        try:
            handle_exit(sio)
            if tracker:
                tracker.running = False
            if sio.connected:
                sio.disconnect()
            self.logged_in = False

            if self.status_label.winfo_exists():
                self.status_label.config(text="Status: Logged Out", fg="red")
            if self.login_btn.winfo_exists():
                self.login_btn.config(text="Login", state="normal")
        except Exception as e:
            print("Logout error:", e)

    def show_signup(self):
        signup = tk.Toplevel()
        signup.title("Sign Up")
        signup.geometry("400x300")
        signup.configure(bg="#fff")

        tk.Label(signup, text="Create Account", font=("Segoe UI", 16, "bold")).pack(pady=20)
        tk.Label(signup, text="Email").pack()
        tk.Entry(signup).pack()
        tk.Label(signup, text="New Password").pack()
        tk.Entry(signup, show="*").pack()
        tk.Button(signup, text="Sign Up", bg="#28a745", fg="white", width=15).pack(pady=20)

    def show_forgot(self):
        forgot = tk.Toplevel()
        forgot.title("Password Recovery")
        forgot.geometry("400x250")
        forgot.configure(bg="#fff")

        tk.Label(forgot, text="Recover Password", font=("Segoe UI", 16, "bold")).pack(pady=20)
        tk.Label(forgot, text="Registered Email").pack()
        tk.Entry(forgot).pack()
        tk.Button(forgot, text="Send Recovery Email", bg="#007bff", fg="white", width=20).pack(pady=20)

    def on_exit(self):
        if self.logged_in:
            self.logout()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WorkforceApp(root)
    root.mainloop()

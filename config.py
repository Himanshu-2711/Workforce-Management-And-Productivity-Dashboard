EMPLOYEE_ID = "EMP123"  # Replace with dynamic assignment if needed
DASHBOARD_API_URL = "http://localhost:5000/sendStatus"  # REST API fallback

def get_ip_location():
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    return "Office" if ip.startswith("192.168.") else "Work From Home"

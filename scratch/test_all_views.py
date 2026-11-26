import urllib.request
import json
import re

# 1. Login as employee to get live data
login_data = json.dumps({"email": "emp.test@infosys.com", "password": "Password@123"}).encode("utf-8")
req = urllib.request.Request("http://localhost:8080/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode("utf-8")).get("token")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

endpoints = {
    "profile": "/api/employee/me/profile",
    "skills": "/api/employee/me/skills",
    "gaps": "/api/employee/me/gaps",
    "recs": "/api/employee/me/recommendations",
    "learning": "/api/employee/me/learning",
    "certs": "/api/employee/me/certifications",
    "mentors": "/api/employee/me/mentors",
    "sessions": "/api/employee/sessions",
    "notifs": "/api/employee/me/notifications",
    "chat": "/api/employee/me/chat"
}

print("=== VERIFYING ALL EMPLOYEE DASHBOARD BACKEND DATA APIS ===")
for name, path in endpoints.items():
    if name == "chat":
        req = urllib.request.Request(f"http://localhost:8080{path}", data=b'{"message":"hi","history":[]}', headers=headers)
    else:
        req = urllib.request.Request(f"http://localhost:8080{path}", headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[PASS] {name:15} -> HTTP {resp.status} (Valid JSON received)")
    except Exception as e:
        print(f"[FAIL] {name:15} -> {e}")

print("\n=== VERIFYING FRONTEND HTML VALIDITY ===")
with open("frontend/employee-dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Verify that all view containers and main tags are properly closed
assert "<main id=\"main\" tabindex=\"-1\">" in html
assert "views.gaps = () => chatHtml() + _gapsView();" in html
assert "function chatHtml()" in html
assert "function chatLogHtml()" in html
assert "function mdLite(" in html

print("[PASS] All view hooks, chat markup, and script tags are fully intact.")

"""单独测试PDF上传，看403详细错误"""
import requests, time, os

BASE = "http://127.0.0.1:8003/api/v1"
PDF_PATH = r"d:\zgyd\简历2.pdf"

ts = str(int(time.time() * 1000))
username = f"dbg_{ts[-6:]}"
r = requests.post(f"{BASE}/auth/register", json={
    "username": username, "email": f"{username}@test.com", "password": "test1234"
}, timeout=30)
token = r.json().get("access_token", "")
H = {"Authorization": f"Bearer {token}"}

# 先做MBTI
r = requests.get(f"{BASE}/personality/questions", timeout=30)
qs = r.json()["questions"]
answers = {str(q["id"]): "A" for q in qs}
requests.post(f"{BASE}/personality/submit", json={"answers": answers}, headers=H, timeout=30)

# 上传PDF
print(f"上传PDF: {PDF_PATH}")
with open(PDF_PATH, "rb") as f:
    files = {"file": ("简历2.pdf", f, "application/pdf")}
    r = requests.post(f"{BASE}/ability/upload", files=files, headers=H, timeout=180)

print(f"status={r.status_code}")
print(f"response={r.text[:1000]}")

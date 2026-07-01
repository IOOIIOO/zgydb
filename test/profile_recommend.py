"""Recommend 分步耗时分析"""
import time, requests, json

BASE = "http://127.0.0.1:8000/api/v1"

# 注册
ts = str(int(time.time() * 1000))
u = f"prof_{ts[-6:]}"
r = requests.post(f"{BASE}/auth/register", json={
    "username": u, "email": f"{u}@test.com", "password": "test1234"
}, timeout=30)
token = r.json().get("access_token", "")
H = {"Authorization": f"Bearer {token}"}
print(f"[Register] {u}")

# 准备前置数据：MBTI + Ability
r = requests.get(f"{BASE}/personality/questions", timeout=30)
qs = r.json()["questions"]
answers = {str(q["id"]): "A" for q in qs}
requests.post(f"{BASE}/personality/submit", json={"answers": answers}, headers=H, timeout=30)
print("[Step1 MBTI] done")

desc = "本科学历，计算机科学与技术专业，学过HTML/CSS/JavaScript基础，会用Photoshop做简单切图，在学校做过一个简单的个人博客项目，CET-4 425分通过，无实习经验，无竞赛经历"
t0 = time.time()
requests.post(f"{BASE}/ability/describe", json={"text": desc}, headers=H, timeout=120)
print(f"[Step2 Ability] {time.time()-t0:.1f}s")

# 现在直接调用推荐接口，但用日志追踪各步骤
# 由于不能侵入式改代码，先调用一次 warm-up embedding
print("\n=== Warm-up embedding 模型 ===")
t0 = time.time()
# 第一次调用让模型加载
requests.post(f"{BASE}/recommendation/recommend", json={"direction_id": 1}, headers=H, timeout=120)
print(f"Warm-up: {time.time()-t0:.1f}s")

# 第二次调用：embedding 已加载，应该更快
print("\n=== 第二次调用（embedding 已加载）===")
t0 = time.time()
r = requests.post(f"{BASE}/recommendation/recommend", json={"direction_id": 1}, headers=H, timeout=120)
elapsed = time.time() - t0
print(f"Recommend (warm): {elapsed:.1f}s status={r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  count={len(data) if isinstance(data, list) else 'N/A'}")

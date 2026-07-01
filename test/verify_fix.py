"""验证修复后的完整流程测试"""
import requests, json, time, os

BASE = "http://127.0.0.1:8000/api/v1"

def safe_json(r):
    try: return r.json()
    except: return {"_raw": r.text[:500]}

ts = str(int(time.time() * 1000))
username = f"verify_{ts[-6:]}"

# Step 0: Register
r = requests.post(f"{BASE}/auth/register", json={
    "username": username, "email": f"{username}@test.com", "password": "test1234"
}, timeout=30)
reg = safe_json(r)
token = reg.get("access_token", "")
H = {"Authorization": f"Bearer {token}"}
print(f"[Register] status={r.status_code} user={username}")

# Step 1: MBTI
r = requests.get(f"{BASE}/personality/questions", timeout=30)
qs = r.json()["questions"]
answers = {str(q["id"]): "A" for q in qs}
r = requests.post(f"{BASE}/personality/submit", json={"answers": answers}, headers=H, timeout=30)
mbti = safe_json(r)
print(f"[Step1 MBTI] status={r.status_code} type={mbti.get('personality_type')} intensity_level={mbti.get('intensity_level')}")

# Step 2: Ability Assessment
desc = "本科学历，计算机科学与技术专业，学过HTML/CSS/JavaScript基础，会用Photoshop做简单切图，在学校做过一个简单的个人博客项目，CET-4 425分通过，无实习经验，无竞赛经历"
t0 = time.time()
r = requests.post(f"{BASE}/ability/describe", json={"text": desc}, headers=H, timeout=120)
elapsed = time.time() - t0
ability = safe_json(r)
print(f"[Step2 Ability] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    print(f"  edu={ability.get('education')} k={ability.get('knowledge_score')} t={ability.get('tool_score')} p={ability.get('project_score')}")
    print(f"  certs={len(ability.get('certificates', []))} comps={len(ability.get('competitions', []))}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 3: Job Recommendation
t0 = time.time()
r = requests.post(f"{BASE}/recommendation/recommend", json={"direction_id": 1}, headers=H, timeout=120)
elapsed = time.time() - t0
positions = safe_json(r)
print(f"[Step3 Recommend] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    pos_list = positions if isinstance(positions, list) else positions.get("positions", [])
    titles = [p.get("title", "") for p in pos_list]
    reasons = [p.get("recommendation_reason", "") or "" for p in pos_list]
    non_empty_reasons = sum(1 for x in reasons if x.strip())
    print(f"  count={len(pos_list)} non_empty_reasons={non_empty_reasons}")
    if reasons:
        for i, reason in enumerate(reasons[:3]):
            print(f"  reason[{i}]: {reason[:80]}...")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 4a: Trend Analysis
t0 = time.time()
r = requests.post(f"{BASE}/trend/analyze", json={"direction_id": 1, "position_id": None}, headers=H, timeout=180)
elapsed = time.time() - t0
trend = safe_json(r)
print(f"[Step4a Trend] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    td = trend.get("trend_data", {})
    if isinstance(td, dict):
        print(f"  overview: {str(td.get('overview', ''))[:60]}...")
        print(f"  tech_impact: {str(td.get('tech_impact', ''))[:60]}...")
        print(f"  salary_trend: {str(td.get('salary_trend', ''))[:60]}...")
        print(f"  trends array: {len(td.get('trends', []))} items")
    print(f"  risk_warnings: {len(trend.get('risk_warnings', []))} items")
    print(f"  info_sources: {len(trend.get('info_sources', []))} items")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 4b: Development Path
t0 = time.time()
r = requests.post(f"{BASE}/development/generate", json={"direction_id": 1, "position_id": None}, headers=H, timeout=180)
elapsed = time.time() - t0
dev = safe_json(r)
print(f"[Step4b DevPath] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    resources = dev.get("resource_list", [])
    print(f"  short_term goal: {str(dev.get('short_term_path', {}).get('goal', ''))[:60]}...")
    print(f"  resources: {len(resources)}")
    if resources:
        for res in resources[:3]:
            name = res.get("name", "")
            url = res.get("url", "")
            print(f"    - name={name[:40]} url_empty={not url.strip()}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 5: Report
t0 = time.time()
r = requests.post(f"{BASE}/report/generate", headers=H, timeout=180)
elapsed = time.time() - t0
report = safe_json(r)
print(f"[Step5 Report] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    pdf_path = report.get("pdf_path", "")
    print(f"  pdf_path={pdf_path}")
    if pdf_path:
        print(f"  pdf exists: {os.path.exists(pdf_path)}")
    rd = report.get("report_data", {})
    if rd:
        polished = rd.get("polished", "")
        print(f"  polished length: {len(polished)}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Progress
r = requests.get(f"{BASE}/progress", headers=H, timeout=30)
prog = safe_json(r)
print(f"\n[Progress] steps: 1={prog.get('step1_completed')} 2={prog.get('step2_completed')} 3={prog.get('step3_completed')} 4={prog.get('step4_completed')} 5={prog.get('step5_completed')}")

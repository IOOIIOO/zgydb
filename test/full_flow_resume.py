"""用真实简历走完整流程测试"""
import requests, time, os, json

BASE = "http://127.0.0.1:8000/api/v1"
PDF_PATH = r"d:\zgyd\简历2.pdf"

def safe_json(r):
    try: return r.json()
    except: return {"_raw": r.text[:500]}

ts = str(int(time.time() * 1000))
username = f"resume_{ts[-6:]}"

# Step 0: Register
r = requests.post(f"{BASE}/auth/register", json={
    "username": username, "email": f"{username}@test.com", "password": "test1234"
}, timeout=30)
reg = safe_json(r)
token = reg.get("access_token", "")
H = {"Authorization": f"Bearer {token}"}
print(f"[Register] status={r.status_code} user={username}")

if not os.path.exists(PDF_PATH):
    print(f"ERROR: 简历文件不存在: {PDF_PATH}")
    exit(1)
print(f"[PDF] 找到简历: {PDF_PATH} size={os.path.getsize(PDF_PATH)}B")

# Step 1: MBTI
r = requests.get(f"{BASE}/personality/questions", timeout=30)
qs = r.json()["questions"]
answers = {str(q["id"]): "A" for q in qs}
r = requests.post(f"{BASE}/personality/submit", json={"answers": answers}, headers=H, timeout=30)
mbti = safe_json(r)
print(f"\n[Step1 MBTI] status={r.status_code} type={mbti.get('personality_type')} intensity={mbti.get('intensity_level')}")
if r.status_code != 200:
    print(f"  ERROR: {r.text[:300]}")

# Step 2: Ability - 上传真实简历PDF
print(f"\n[Step2 Ability] 上传真实简历...")
t0 = time.time()
with open(PDF_PATH, "rb") as f:
    files = {"file": ("简历2.pdf", f, "application/pdf")}
    r = requests.post(f"{BASE}/ability/upload", files=files, headers=H, timeout=180)
elapsed = time.time() - t0
ability = safe_json(r)
print(f"[Step2 Ability] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    print(f"  edu={ability.get('education')}")
    print(f"  knowledge={ability.get('knowledge_score')} tool={ability.get('tool_score')} project={ability.get('project_score')}")
    print(f"  logic={ability.get('logic_label')} comm={ability.get('communication_label')}")
    print(f"  cert_competition={ability.get('cert_competition_label')} learning={ability.get('learning_label')}")
    certs = ability.get("certificates", [])
    comps = ability.get("competitions", [])
    print(f"  证书数={len(certs)} 竞赛数={len(comps)}")
    for c in certs[:5]:
        print(f"    证书: {c.get('name','')[:40]} level={c.get('level_name','')} score={c.get('score','')}")
    for c in comps[:5]:
        print(f"    竞赛: {c.get('name','')[:40]} level={c.get('level_name','')} bonus={c.get('bonus_score','')}")
    strengths = ability.get("strengths", [])
    weaknesses = ability.get("weaknesses", [])
    print(f"  优势({len(strengths)}): {strengths[:3]}")
    print(f"  短板({len(weaknesses)}): {weaknesses[:3]}")
else:
    print(f"  ERROR: {r.text[:500]}")

# Step 3: Recommend
t0 = time.time()
r = requests.post(f"{BASE}/recommendation/recommend", json={"direction_id": 1}, headers=H, timeout=120)
elapsed = time.time() - t0
positions = safe_json(r)
print(f"\n[Step3 Recommend] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    pos_list = positions if isinstance(positions, list) else positions.get("positions", [])
    print(f"  count={len(pos_list)}")
    for i, p in enumerate(pos_list[:3]):
        print(f"    [{i+1}] {p.get('title','')[:30]} match={p.get('match_score',0)} city={p.get('city','')}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 4a: Trend
t0 = time.time()
r = requests.post(f"{BASE}/trend/analyze", json={"direction_id": 1, "position_id": None}, headers=H, timeout=180)
elapsed = time.time() - t0
trend = safe_json(r)
print(f"\n[Step4a Trend] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    td = trend.get("trend_data", {})
    if isinstance(td, dict):
        print(f"  overview: {str(td.get('overview', ''))[:80]}...")
        print(f"  dimensions: {len(td.get('trends', []))} items")
    print(f"  risks: {len(trend.get('risk_warnings', []))} sources: {len(trend.get('info_sources', []))}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 4b: DevPath
t0 = time.time()
r = requests.post(f"{BASE}/development/generate", json={"direction_id": 1, "position_id": None}, headers=H, timeout=180)
elapsed = time.time() - t0
dev = safe_json(r)
print(f"\n[Step4b DevPath] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    short = dev.get("short_term_path", {})
    print(f"  short goal: {str(short.get('goal',''))[:60]}...")
    resources = dev.get("resource_list", [])
    print(f"  resources: {len(resources)}")
    for res in resources[:3]:
        name = res.get("name", "")
        url = res.get("url", "")
        print(f"    - {name[:30]} url_empty={not url.strip()}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 5: Report
t0 = time.time()
r = requests.post(f"{BASE}/report/generate", headers=H, timeout=180)
elapsed = time.time() - t0
report = safe_json(r)
print(f"\n[Step5 Report] status={r.status_code} time={elapsed:.1f}s")
if r.status_code == 200:
    pdf_path = report.get("pdf_path", "")
    print(f"  pdf_path={pdf_path}")
    if pdf_path:
        print(f"  pdf exists: {os.path.exists(pdf_path)}")
    rd = report.get("report_data", {})
    if rd:
        polished = rd.get("polished", "")
        print(f"  polished length: {len(polished)}")
        if polished:
            print(f"  preview: {polished[:200]}...")
else:
    print(f"  ERROR: {r.text[:300]}")

# Progress
r = requests.get(f"{BASE}/progress", headers=H, timeout=30)
prog = safe_json(r)
print(f"\n[Progress] 1={prog.get('step1_completed')} 2={prog.get('step2_completed')} 3={prog.get('step3_completed')} 4={prog.get('step4_completed')} 5={prog.get('step5_completed')}")

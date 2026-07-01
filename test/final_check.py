import requests, time, os

BASE = "http://127.0.0.1:8000/api/v1"

def safe_json(r):
    try: return r.json()
    except: return {"_raw": r.text[:500]}

ts = str(int(time.time() * 1000))
r = requests.post(f'{BASE}/auth/register', json={
    'username': f'final_{ts[-6:]}', 'email': f'final_{ts[-6:]}@test.com', 'password': 'test1234'
})
token = r.json()['access_token']
H = {'Authorization': f'Bearer {token}'}

# Step 1: MBTI
r = requests.get(f'{BASE}/personality/questions')
qs = r.json()['questions']
answers = {str(q['id']): 'A' for q in qs}
requests.post(f'{BASE}/personality/submit', json={'answers': answers}, headers=H)
print('[OK] Step1 MBTI')

# Step 2: Ability
desc = '本科学历，计算机科学与技术专业，学过HTML/CSS/JavaScript基础，会用Photoshop做简单切图，在学校做过一个简单的个人博客项目，CET-4 425分通过，无实习经验，无竞赛经历'
t0 = time.time()
r = requests.post(f'{BASE}/ability/describe', json={'text': desc}, headers=H, timeout=120)
print(f'[Step2] Ability: status={r.status_code} time={time.time()-t0:.1f}s')
ability = safe_json(r)
if r.status_code == 200:
    print(f'  edu={ability.get("education")} k={ability.get("knowledge_score")} t={ability.get("tool_score")} p={ability.get("project_score")}')
    print(f'  certs={len(ability.get("certificates", []))} comps={len(ability.get("competitions", []))}')
else:
    print(f'  ERROR: {r.text[:300]}')

# Step 3: Recommendation
t0 = time.time()
r = requests.post(f'{BASE}/recommendation/recommend', json={'direction_id': 1}, headers=H, timeout=120)
print(f'[Step3] Recommend: status={r.status_code} time={time.time()-t0:.1f}s')
positions = safe_json(r)
if r.status_code == 200:
    pos_list = positions if isinstance(positions, list) else positions.get("positions", [])
    titles = [p.get("title", "") for p in pos_list]
    unique_titles = len(set(titles))
    reasons = [p.get("recommendation_reason", "") or "" for p in pos_list]
    non_empty_reasons = sum(1 for x in reasons if x.strip())
    print(f'  count={len(pos_list)} unique_titles={unique_titles} non_empty_reasons={non_empty_reasons}')
    print(f'  titles: {list(dict.fromkeys(titles))[:5]}')
    scores = [p.get("match_score", 0) for p in pos_list]
    print(f'  score range: {min(scores):.1f} - {max(scores):.1f}')
else:
    print(f'  ERROR: {r.text[:300]}')

# Step 4a: Trend Analysis (test 2 times)
for i in range(2):
    t0 = time.time()
    r = requests.post(f'{BASE}/trend/analyze', json={'direction_id': 1, 'position_id': None}, headers=H, timeout=180)
    elapsed = time.time() - t0
    print(f'[Step4a] Trend attempt {i+1}: status={r.status_code} time={elapsed:.1f}s')
    if r.status_code != 200:
        print(f'  ERROR: {r.text[:300]}')
    else:
        trend = safe_json(r)
        td = trend.get("trend_data", {})
        if isinstance(td, dict):
            print(f'  trends count: {len(td.get("trends", []))}')
            print(f'  resources count: {len(td.get("resources", []))}')
        print(f'  info_sources count: {len(trend.get("info_sources", []))}')
        print(f'  risk_warnings count: {len(trend.get("risk_warnings", []))}')

# Step 4b: Development Path
t0 = time.time()
r = requests.post(f'{BASE}/development/generate', json={'direction_id': 1, 'position_id': None}, headers=H, timeout=180)
elapsed = time.time() - t0
print(f'[Step4b] Development: status={r.status_code} time={elapsed:.1f}s')
if r.status_code != 200:
    print(f'  ERROR: {r.text[:300]}')
else:
    dev = safe_json(r)
    print(f'  resource_list count: {len(dev.get("resource_list", []))}')
    if dev.get("resource_list"):
        for res in dev["resource_list"][:3]:
            print(f'    - {res.get("name", "")[:40]} | type={res.get("type", "")} | url_empty={not res.get("url", "").strip()}')

# Step 5: Report Generation
t0 = time.time()
r = requests.post(f'{BASE}/report/generate', headers=H, timeout=180)
elapsed = time.time() - t0
print(f'[Step5] Report: status={r.status_code} time={elapsed:.1f}s')
if r.status_code != 200:
    print(f'  ERROR: {r.text[:300]}')
else:
    report = safe_json(r)
    print(f'  id={report.get("id")} version={report.get("version")}')
    print(f'  pdf_path={report.get("pdf_path")}')
    pdf_path = report.get("pdf_path", "")
    if pdf_path:
        print(f'  pdf exists: {os.path.exists(pdf_path)}')
        if os.path.exists(pdf_path):
            print(f'  pdf size: {os.path.getsize(pdf_path)} bytes')
    rd = report.get("report_data", {})
    if rd:
        print(f'  polished length: {len(rd.get("polished", "")) if rd.get("polished") else 0}')
        print(f'  has personality: {bool(rd.get("personality"))}')
        print(f'  has ability: {bool(rd.get("ability"))}')
        print(f'  recommendations count: {len(rd.get("recommendations", []))}')
        print(f'  has trend: {bool(rd.get("trend"))}')
        print(f'  has path: {bool(rd.get("path"))}')

# Progress
r = requests.get(f'{BASE}/progress', headers=H)
prog = safe_json(r)
print(f'\n[Progress]')
for key in ['step1_completed', 'step2_completed', 'step3_completed', 'step4_completed', 'step5_completed', 'current_step']:
    print(f'  {key}: {prog.get(key)}')

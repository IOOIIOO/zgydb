import requests, time, os

BASE = "http://127.0.0.1:8000/api/v1"

ts = str(int(time.time() * 1000))
r = requests.post(f'{BASE}/auth/register', json={
    'username': f'final_{ts[-6:]}', 'email': f'final_{ts[-6:]}@test.com', 'password': 'test1234'
})
token = r.json()['access_token']
H = {'Authorization': f'Bearer {token}'}
uid = r.json()['user']['id']

# Step 1: MBTI
r = requests.get(f'{BASE}/personality/questions')
qs = r.json()['questions']
answers = {str(q['id']): 'A' for q in qs}
requests.post(f'{BASE}/personality/submit', json={'answers': answers}, headers=H)
print('Step1 MBTI done')

# Step 2: Ability
desc = '本科学历，计算机科学与技术专业，学过HTML/CSS/JavaScript基础，会用Photoshop做简单切图，在学校做过一个简单的个人博客项目，CET-4 425分通过，无实习经验，无竞赛经历'
r = requests.post(f'{BASE}/ability/describe', json={'text': desc}, headers=H, timeout=120)
print(f'Step2 Ability done: status={r.status_code}')

# Step 3: Recommendation
r = requests.post(f'{BASE}/recommendation/recommend', json={'direction_id': 1}, headers=H, timeout=120)
print(f'Step3 Recommend done: status={r.status_code}, count={len(r.json())}')

# Step 4a: Trend
print('Running trend analysis...')
t0 = time.time()
r = requests.post(f'{BASE}/trend/analyze', json={'direction_id': 1, 'position_id': 0}, headers=H, timeout=120)
elapsed = time.time() - t0
print(f'Step4a Trend done: status={r.status_code} time={elapsed:.1f}s')
trend = r.json()
print(f'  trend keys: {list(trend.keys())}')
print(f'  trend_data keys: {list(trend.get("trend_data", {}).keys()) if isinstance(trend.get("trend_data"), dict) else type(trend.get("trend_data"))}')
td = trend.get("trend_data", {})
if isinstance(td, dict):
    print(f'  trends count: {len(td.get("trends", []))}')
    print(f'  resources count: {len(td.get("resources", []))}')
print(f'  risk_warnings: {trend.get("risk_warnings", [])}')
print(f'  info_sources count: {len(trend.get("info_sources", []))}')
if trend.get("info_sources"):
    for s in trend["info_sources"][:2]:
        print(f'    - {s.get("title", "")[:40]} | {s.get("url", "")[:60]}')

# Step 4b: Development
print('\nRunning development path...')
t0 = time.time()
r = requests.post(f'{BASE}/development/generate', json={'direction_id': 1, 'position_id': 0}, headers=H, timeout=120)
elapsed = time.time() - t0
print(f'Step4b Dev done: status={r.status_code} time={elapsed:.1f}s')
dev = r.json()
print(f'  dev keys: {list(dev.keys())}')
print(f'  resource_list count: {len(dev.get("resource_list", []))}')
if dev.get("resource_list"):
    for r in dev["resource_list"][:2]:
        print(f'    - name={r.get("name", "")[:40]} | type={r.get("type", "")} | url={r.get("url", "")[:60]}')

# Step 5: Report
print('\nGenerating report...')
t0 = time.time()
r = requests.post(f'{BASE}/report/generate', headers=H, timeout=120)
elapsed = time.time() - t0
print(f'Step5 Report done: status={r.status_code} time={elapsed:.1f}s')
report = r.json()
print(f'  report keys: {list(report.keys())}')
print(f'  id={report.get("id")}')
print(f'  version={report.get("version")}')
print(f'  pdf_path={report.get("pdf_path")}')
pdf_path = report.get("pdf_path", "")
if pdf_path:
    print(f'  pdf exists: {os.path.exists(pdf_path)}')
    if os.path.exists(pdf_path):
        print(f'  pdf size: {os.path.getsize(pdf_path)} bytes')
rd = report.get("report_data", {})
if rd:
    print(f'  report_data keys: {list(rd.keys())}')
    print(f'  polished length: {len(rd.get("polished", "")) if rd.get("polished") else 0}')

# Progress check
print('\nProgress:')
r = requests.get(f'{BASE}/progress', headers=H)
prog = r.json()
for key in ['step1_completed', 'step2_completed', 'step3_completed', 'step4_completed', 'step5_completed']:
    print(f'  {key}: {prog.get(key)}')

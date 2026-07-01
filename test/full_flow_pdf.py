"""完整流程测试 - 真实简历PDF版"""
import requests, time, os, json

BASE = "http://127.0.0.1:8000/api/v1"
PDF_PATH = r"d:\zgyd\简历2.pdf"

def safe_json(r):
    try: return r.json()
    except: return {"_raw": r.text[:500]}

total_start = time.time()
ts = str(int(time.time() * 1000))
username = f"pdf_{ts[-6:]}"

# Register
t0 = time.time()
r = requests.post(f"{BASE}/auth/register", json={
    "username": username, "email": f"{username}@test.com", "password": "test1234"
}, timeout=30)
token = safe_json(r).get("access_token", "")
H = {"Authorization": f"Bearer {token}"}
print(f"[Register] {username} {time.time()-t0:.1f}s")

if not os.path.exists(PDF_PATH):
    print(f"ERROR: 简历不存在: {PDF_PATH}")
    exit(1)
print(f"[PDF] {PDF_PATH} size={os.path.getsize(PDF_PATH)}B")

# Step 1: MBTI
t0 = time.time()
r = requests.get(f"{BASE}/personality/questions", timeout=30)
qs = r.json()["questions"]
answers = {str(q["id"]): "A" for q in qs}
r = requests.post(f"{BASE}/personality/submit", json={"answers": answers}, headers=H, timeout=30)
mbti = safe_json(r)
t1 = time.time() - t0
print(f"\n[Step1 MBTI] {r.status_code} {t1:.1f}s type={mbti.get('personality_type')} intensity={mbti.get('intensity_level')}")
if r.status_code == 200:
    print(f"  EI={mbti.get('ei_score')} SN={mbti.get('sn_score')} TF={mbti.get('tf_score')} JP={mbti.get('jp_score')}")
    print(f"  优势: {mbti.get('strengths',[])[:2]}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 2: Ability - 上传真实简历PDF
t0 = time.time()
with open(PDF_PATH, "rb") as f:
    files = {"file": ("简历2.pdf", f, "application/pdf")}
    r = requests.post(f"{BASE}/ability/upload", files=files, headers=H, timeout=180)
t2 = time.time() - t0
ability = safe_json(r)
print(f"\n[Step2 Ability] {r.status_code} {t2:.1f}s")
if r.status_code == 200:
    print(f"  学历={ability.get('education')}")
    print(f"  知识={ability.get('knowledge_score')} 工具={ability.get('tool_score')} 项目={ability.get('project_score')}")
    print(f"  逻辑={ability.get('logic_label')} 沟通={ability.get('communication_label')} 证书竞赛={ability.get('cert_competition_label')} 学习={ability.get('learning_label')}")
    certs = ability.get("certificates", [])
    comps = ability.get("competitions", [])
    print(f"  证书({len(certs)}):")
    for c in certs:
        print(f"    - {c.get('name','')[:30]} [{c.get('level_name','')}] 分={c.get('score','')}")
    print(f"  竞赛({len(comps)}):")
    for c in comps:
        print(f"    - {c.get('name','')[:30]} [{c.get('level_name','')}] 加分={c.get('bonus_score','')}")
    print(f"  优势: {ability.get('strengths',[])[:3]}")
    print(f"  短板: {ability.get('weaknesses',[])[:3]}")
else:
    print(f"  ERROR: {r.text[:500]}")

# Step 3: Recommend
t0 = time.time()
r = requests.post(f"{BASE}/recommendation/recommend", json={"direction_id": 1}, headers=H, timeout=120)
t3 = time.time() - t0
positions = safe_json(r)
print(f"\n[Step3 Recommend] {r.status_code} {t3:.1f}s")
if r.status_code == 200:
    pos_list = positions if isinstance(positions, list) else positions.get("positions", [])
    print(f"  推荐岗位数={len(pos_list)}")
    for i, p in enumerate(pos_list[:3]):
        print(f"    [{i+1}] {p.get('title','')[:25]} 匹配={p.get('match_score',0)} {p.get('city','')}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 4a: Trend
t0 = time.time()
r = requests.post(f"{BASE}/trend/analyze", json={"direction_id": 1, "position_id": None}, headers=H, timeout=180)
t4a = time.time() - t0
trend = safe_json(r)
print(f"\n[Step4a Trend] {r.status_code} {t4a:.1f}s")
if r.status_code == 200:
    td = trend.get("trend_data", {})
    print(f"  6维度: overview={bool(td.get('overview'))} tech={bool(td.get('tech_impact'))} regional={bool(td.get('regional_demand'))}")
    print(f"         salary={bool(td.get('salary_trend'))} barrier={bool(td.get('entry_barrier'))} personal={bool(td.get('personal_analysis'))}")
    print(f"  风险={len(trend.get('risk_warnings',[]))} 来源={len(trend.get('info_sources',[]))}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 4b: DevPath
t0 = time.time()
r = requests.post(f"{BASE}/development/generate", json={"direction_id": 1, "position_id": None}, headers=H, timeout=180)
t4b = time.time() - t0
dev = safe_json(r)
print(f"\n[Step4b DevPath] {r.status_code} {t4b:.1f}s")
if r.status_code == 200:
    short = dev.get("short_term_path", {})
    print(f"  短期: {short.get('duration','')} - {str(short.get('goal',''))[:40]}")
    resources = dev.get("resource_list", [])
    print(f"  资源({len(resources)}):")
    for res in resources[:3]:
        print(f"    - {res.get('name','')[:25]} url={'有' if res.get('url','').strip() else '空'}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 5: Report
t0 = time.time()
r = requests.post(f"{BASE}/report/generate", headers=H, timeout=180)
t5 = time.time() - t0
report = safe_json(r)
print(f"\n[Step5 Report] {r.status_code} {t5:.1f}s")
if r.status_code == 200:
    pdf_path = report.get("pdf_path", "")
    print(f"  PDF: {os.path.basename(pdf_path)} 存在={os.path.exists(pdf_path) if pdf_path else False}")
    rd = report.get("report_data", {})
    polished = rd.get("polished", "")
    print(f"  润色报告: {len(polished)}字")
else:
    print(f"  ERROR: {r.text[:300]}")

total = time.time() - total_start
print(f"\n{'='*50}")
print(f"总耗时: {total:.1f}s")
print(f"  Step1 MBTI:     {t1:.1f}s")
print(f"  Step2 Ability:  {t2:.1f}s (PDF上传)")
print(f"  Step3 Recommend:{t3:.1f}s")
print(f"  Step4a Trend:   {t4a:.1f}s")
print(f"  Step4b DevPath: {t4b:.1f}s")
print(f"  Step5 Report:   {t5:.1f}s")
print(f"{'='*50}")

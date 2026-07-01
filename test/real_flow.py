"""完整流程测试（文字描述版，模拟真实用户）"""
import requests, time, os

BASE = "http://127.0.0.1:8002/api/v1"

def safe_json(r):
    try: return r.json()
    except: return {"_raw": r.text[:500]}

ts = str(int(time.time() * 1000))
username = f"real_{ts[-6:]}"

# Register
r = requests.post(f"{BASE}/auth/register", json={
    "username": username, "email": f"{username}@test.com", "password": "test1234"
}, timeout=30)
token = safe_json(r).get("access_token", "")
H = {"Authorization": f"Bearer {token}"}
print(f"[Register] {username}")

# Step 1: MBTI - 模拟真实作答（混合选择）
r = requests.get(f"{BASE}/personality/questions", timeout=30)
qs = r.json()["questions"]
# 真实作答：前20题选A，后20题选B
answers = {}
for i, q in enumerate(qs):
    answers[str(q["id"])] = "A" if i < 20 else "B"
r = requests.post(f"{BASE}/personality/submit", json={"answers": answers}, headers=H, timeout=30)
mbti = safe_json(r)
print(f"\n[Step1 MBTI] {r.status_code} type={mbti.get('personality_type')} intensity={mbti.get('intensity_level')}")
if r.status_code == 200:
    print(f"  EI={mbti.get('ei_score')} SN={mbti.get('sn_score')} TF={mbti.get('tf_score')} JP={mbti.get('jp_score')}")
    print(f"  优势: {mbti.get('strengths',[])[:2]}")
    print(f"  方向: {mbti.get('direction_tendencies',[])[:3]}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 2: Ability - 真实文字描述
desc = "我是计算机科学与技术专业的本科大三学生，GPA 3.5/4.0。掌握Python、Java、JavaScript编程语言，熟悉React前端框架和Node.js后端开发。使用过MySQL、Redis数据库。做过两个项目：一个是基于React的在线商城前端，负责商品展示和购物车模块；另一个是基于Spring Boot的后台管理系统，负责权限管理和数据统计模块。获得过蓝桥杯省赛二等奖，通过CET-6，有AWS云从业者认证。曾在某互联网公司暑期实习3个月，担任前端开发实习生。"
t0 = time.time()
r = requests.post(f"{BASE}/ability/describe", json={"text": desc}, headers=H, timeout=120)
elapsed = time.time() - t0
ability = safe_json(r)
print(f"\n[Step2 Ability] {r.status_code} {elapsed:.1f}s")
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
elapsed = time.time() - t0
positions = safe_json(r)
print(f"\n[Step3 Recommend] {r.status_code} {elapsed:.1f}s")
if r.status_code == 200:
    pos_list = positions if isinstance(positions, list) else positions.get("positions", [])
    print(f"  推荐岗位数={len(pos_list)}")
    for i, p in enumerate(pos_list[:5]):
        print(f"    [{i+1}] {p.get('title','')[:25]} 匹配度={p.get('match_score',0)} 城市={p.get('city','')} 薪资={p.get('salary_range','')}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 4a: Trend
t0 = time.time()
r = requests.post(f"{BASE}/trend/analyze", json={"direction_id": 1, "position_id": None}, headers=H, timeout=180)
elapsed = time.time() - t0
trend = safe_json(r)
print(f"\n[Step4a Trend] {r.status_code} {elapsed:.1f}s")
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
elapsed = time.time() - t0
dev = safe_json(r)
print(f"\n[Step4b DevPath] {r.status_code} {elapsed:.1f}s")
if r.status_code == 200:
    short = dev.get("short_term_path", {})
    mid = dev.get("mid_term_path", {})
    long_p = dev.get("long_term_path", {})
    print(f"  短期: {short.get('duration','')} - {str(short.get('goal',''))[:50]}")
    print(f"  中期: {mid.get('duration','')} - {str(mid.get('goal',''))[:50]}")
    print(f"  长期: {long_p.get('duration','')} - {str(long_p.get('goal',''))[:50]}")
    resources = dev.get("resource_list", [])
    print(f"  资源({len(resources)}):")
    for res in resources:
        name = res.get("name", "")
        url = res.get("url", "")
        rtype = res.get("type", "")
        print(f"    - {name[:25]} [{rtype}] url={'有' if url.strip() else '空'}")
else:
    print(f"  ERROR: {r.text[:300]}")

# Step 5: Report
t0 = time.time()
r = requests.post(f"{BASE}/report/generate", headers=H, timeout=180)
elapsed = time.time() - t0
report = safe_json(r)
print(f"\n[Step5 Report] {r.status_code} {elapsed:.1f}s")
if r.status_code == 200:
    pdf_path = report.get("pdf_path", "")
    print(f"  PDF: {pdf_path}")
    if pdf_path:
        print(f"  文件存在: {os.path.exists(pdf_path)}")
    rd = report.get("report_data", {})
    polished = rd.get("polished", "")
    print(f"  润色报告长度: {len(polished)}字")
    if polished:
        print(f"  预览: {polished[:300]}...")
else:
    print(f"  ERROR: {r.text[:300]}")

# Progress
r = requests.get(f"{BASE}/progress", headers=H, timeout=30)
prog = safe_json(r)
print(f"\n[Progress] 1={prog.get('step1_completed')} 2={prog.get('step2_completed')} 3={prog.get('step3_completed')} 4={prog.get('step4_completed')} 5={prog.get('step5_completed')}")
print("\n=== 流程完成 ===")

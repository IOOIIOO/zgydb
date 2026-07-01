"""Full user flow test - all steps"""
import requests, json, time, sys

BASE = "http://127.0.0.1:8000/api/v1"

def safe_json(r):
    try: return r.json()
    except Exception: return {"_raw": r.text[:500]}

def run_full_test(label, desc, direction_id=1):
    print(f"\n{'='*70}")
    print(f"TEST: {label}")
    print(f"{'='*70}")
    
    ts = str(int(time.time() * 1000))
    username = f"full_{label}_{ts[-6:]}"
    
    # Step 0: Register
    print(f"\n--- Step 0: Register ---")
    r = requests.post(f"{BASE}/auth/register", json={
        "username": username, "email": f"{username}@test.com", "password": "test1234"
    }, timeout=30)
    reg = safe_json(r)
    token = reg.get("access_token", "")
    H = {"Authorization": f"Bearer {token}"}
    uid = reg.get("user", {}).get("id")
    print(f"  status={r.status_code} uid={uid} user={username}")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:300]}")
        return
    
    # Step 0b: Quick overview directions
    print(f"\n--- Step 0b: Overview Directions ---")
    r = requests.get(f"{BASE}/overview/directions", timeout=30)
    directions = safe_json(r)
    dirs = directions if isinstance(directions, list) else directions.get("directions", [])
    print(f"  status={r.status_code} count={len(dirs)}")
    if dirs:
        print(f"  first: id={dirs[0].get('id')} name={dirs[0].get('name')}")
    
    # Step 1: MBTI
    print(f"\n--- Step 1: MBTI Personality ---")
    r = requests.get(f"{BASE}/personality/questions", timeout=30)
    qs = safe_json(r)
    questions = qs.get("questions", []) if isinstance(qs, dict) else []
    print(f"  questions: {len(questions)}")
    answers = {str(q["id"]): "A" for q in questions}
    r = requests.post(f"{BASE}/personality/submit", json={"answers": answers}, headers=H, timeout=30)
    mbti = safe_json(r)
    print(f"  status={r.status_code}")
    print(f"  type={mbti.get('personality_type')} intensity={mbti.get('intensity')}")
    print(f"  scores: ei={mbti.get('ei_score')} sn={mbti.get('sn_score')} tf={mbti.get('tf_score')} jp={mbti.get('jp_score')}")
    
    # Step 2: Ability Assessment
    print(f"\n--- Step 2: Ability Assessment ---")
    t0 = time.time()
    r = requests.post(f"{BASE}/ability/describe", json={"text": desc}, headers=H, timeout=120)
    elapsed = time.time() - t0
    ability = safe_json(r)
    print(f"  status={r.status_code} time={elapsed:.1f}s")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:500]}")
    else:
        k = ability.get("knowledge_score")
        t = ability.get("tool_score")
        p = ability.get("project_score")
        edu = ability.get("education")
        certs = ability.get("certificates", [])
        comps = ability.get("competitions", [])
        soft = ability.get("soft_skills", {})
        print(f"  edu={repr(edu)} k={k} t={t} p={p}")
        print(f"  certs ({len(certs)}): {[(c.get('name'), c.get('level_name')) for c in certs]}")
        print(f"  comps ({len(comps)}): {[(c.get('name'), c.get('level_name')) for c in comps]}")
        print(f"  soft_skills keys: {list(soft.keys()) if isinstance(soft, dict) else type(soft)}")
    
    # Step 3: Job Recommendation
    print(f"\n--- Step 3: Job Recommendation ---")
    t0 = time.time()
    r = requests.post(f"{BASE}/recommendation/recommend", json={"direction_id": direction_id}, headers=H, timeout=120)
    elapsed = time.time() - t0
    positions = safe_json(r)
    print(f"  status={r.status_code} time={elapsed:.1f}s")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:500]}")
    else:
        pos_list = positions if isinstance(positions, list) else positions.get("positions", [])
        print(f"  positions: {len(pos_list)}")
        if pos_list:
            titles = [p.get("title", "") for p in pos_list]
            scores = [p.get("match_score", 0) for p in pos_list]
            reasons = [p.get("recommendation_reason", "") or "" for p in pos_list]
            unique_titles = len(set(titles))
            non_empty_reasons = sum(1 for r in reasons if r.strip())
            print(f"  unique titles: {unique_titles}")
            print(f"  non-empty reasons: {non_empty_reasons}")
            print(f"  titles: {titles[:5]}...")
            print(f"  scores: min={min(scores):.1f} max={max(scores):.1f} range={max(scores)-min(scores):.1f}")
            
            # Detail on first position
            pid = pos_list[0]["id"]
            print(f"\n--- Step 3b: Position Detail (id={pid}) ---")
            t0 = time.time()
            r = requests.get(f"{BASE}/recommendation/positions/{pid}/detail", headers=H, timeout=120)
            elapsed = time.time() - t0
            detail = safe_json(r)
            print(f"  status={r.status_code} time={elapsed:.1f}s")
            if r.status_code == 200:
                ma = detail.get("match_analysis", {})
                overall = ma.get("overall_match_score")
                emb = detail.get("embedding_match_score")
                list_score = pos_list[0].get("match_score")
                print(f"  list_score={list_score} overall={overall} embedding={emb}")
                print(f"  gaps={len(ma.get('skill_gaps',[]))} strengths={len(ma.get('strength_points',[]))}")
                reason = ma.get('recommendation_reason', '') or ''
                print(f"  detail reason length: {len(reason)}")
                if reason:
                    print(f"  reason preview: {reason[:100]}...")
    
    # Step 4a: Trend Analysis
    print(f"\n--- Step 4a: Trend Analysis ---")
    t0 = time.time()
    r = requests.post(f"{BASE}/trend/analyze", json={"direction_id": direction_id}, headers=H, timeout=120)
    elapsed = time.time() - t0
    trend = safe_json(r)
    print(f"  status={r.status_code} time={elapsed:.1f}s")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:500]}")
    else:
        dimensions = trend.get("dimensions", [])
        sources = trend.get("sources", [])
        print(f"  dimensions: {len(dimensions)}")
        if dimensions:
            for d in dimensions[:3]:
                print(f"    - {d.get('name', '')}: {str(d.get('trend', ''))[:50]}")
        print(f"  sources: {len(sources)}")
        if sources:
            for s in sources[:3]:
                print(f"    - {s.get('title', '')[:40]} | {s.get('url', '')[:60]}")
        empty_urls = sum(1 for s in sources if not s.get('url', '').strip())
        print(f"  empty source URLs: {empty_urls}/{len(sources)}")
    
    # Step 4b: Development Path
    print(f"\n--- Step 4b: Development Path ---")
    t0 = time.time()
    r = requests.post(f"{BASE}/development/generate", json={"direction_id": direction_id}, headers=H, timeout=120)
    elapsed = time.time() - t0
    dev = safe_json(r)
    print(f"  status={r.status_code} time={elapsed:.1f}s")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:500]}")
    else:
        short_term = dev.get("short_term_path", "")
        mid_term = dev.get("mid_term_path", "")
        long_term = dev.get("long_term_path", "")
        resources = dev.get("resources", [])
        print(f"  short_term: {str(short_term)[:80]}...")
        print(f"  mid_term: {str(mid_term)[:80]}...")
        print(f"  long_term: {str(long_term)[:80]}...")
        print(f"  resources: {len(resources)}")
        if resources:
            for res in resources:
                print(f"    - {res.get('name', '')[:40]} | type={res.get('type', '')} | url={str(res.get('url', ''))[:60]}")
        empty_res_urls = sum(1 for r in resources if not r.get('url', '').strip())
        print(f"  empty resource URLs: {empty_res_urls}/{len(resources)}")
    
    # Step 5: Report Generation
    print(f"\n--- Step 5: Report Generation ---")
    t0 = time.time()
    r = requests.post(f"{BASE}/report/generate", json={"direction_id": direction_id}, headers=H, timeout=120)
    elapsed = time.time() - t0
    report = safe_json(r)
    print(f"  status={r.status_code} time={elapsed:.1f}s")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:500]}")
    else:
        pdf_path = report.get("pdf_path", "")
        report_id = report.get("report_id", "")
        summary = report.get("summary", "")
        print(f"  report_id={report_id}")
        print(f"  pdf_path={repr(pdf_path)}")
        print(f"  summary length: {len(summary) if summary else 0}")
        if summary:
            print(f"  summary preview: {summary[:100]}...")
    
    # Progress check
    print(f"\n--- Progress Check ---")
    r = requests.get(f"{BASE}/progress", headers=H, timeout=30)
    prog = safe_json(r)
    print(f"  status={r.status_code}")
    if r.status_code == 200:
        for key in ["step1_completed", "step2_completed", "step3_completed", "step4_completed", "step5_completed"]:
            print(f"  {key}: {prog.get(key)}")
    
    return True


# ====== RUN ======
master_desc = "北京大学人工智能专业硕士，精通PyTorch和TensorFlow深度学习框架，发表过2篇CCF-A论文，在字节跳动算法岗实习6个月，参加过ACM区域赛获得银牌，CET-6 580分"

run_full_test("MASTER", master_desc, direction_id=1)

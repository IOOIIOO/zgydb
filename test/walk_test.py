"""Full user flow test - compare master vs bachelor students"""
import requests, json, time, sys, os
from collections import Counter

BASE = "http://127.0.0.1:8000/api/v1"

def safe_json(r):
    try: return r.json()
    except Exception: return {"_raw": r.text[:500]}

def run_test(label, desc, direction_id=1):
    ts = str(int(time.time() * 1000))
    username = f"v_{label}_{ts[-6:]}"

    # Register
    r = requests.post(f"{BASE}/auth/register", json={
        "username": username, "email": f"{username}@test.com", "password": "test1234"
    }, timeout=30)
    reg = safe_json(r)
    token = reg.get("access_token", "")
    H = {"Authorization": f"Bearer {token}"}
    uid = reg.get("user", {}).get("id")
    print(f"[{label}] uid={uid} user={username}")

    # MBTI
    r = requests.get(f"{BASE}/personality/questions", timeout=30)
    qs = safe_json(r)
    questions = qs.get("questions", []) if isinstance(qs, dict) else []
    answers = {str(q["id"]): "A" for q in questions}
    r = requests.post(f"{BASE}/personality/submit", json={"answers": answers}, headers=H, timeout=30)
    mbti = safe_json(r)
    print(f"[{label}] MBTI={mbti.get('personality_type')}")

    # Ability
    r = requests.post(f"{BASE}/ability/describe", json={"text": desc}, headers=H, timeout=120)
    ability = safe_json(r)
    print(f"[{label}] Ability status={r.status_code}")
    if r.status_code != 200:
        print(f"  ERROR: {r.text[:300]}")
        return None
    k = ability.get("knowledge_score")
    t = ability.get("tool_score")
    p = ability.get("project_score")
    edu = ability.get("education")
    certs = [(c.get("name"), c.get("level_name")) for c in ability.get("certificates", [])]
    comps = [(c.get("name"), c.get("level_name")) for c in ability.get("competitions", [])]
    print(f"  edu={edu} k={k} t={t} p={p}")
    print(f"  certs={certs}")
    print(f"  comps={comps}")

    # Recommend
    t0 = time.time()
    r = requests.post(f"{BASE}/recommendation/recommend", json={"direction_id": direction_id}, headers=H, timeout=120)
    positions = safe_json(r)
    elapsed = time.time() - t0
    print(f"[{label}] Recommend: {len(positions) if isinstance(positions, list) else 0} positions in {elapsed:.1f}s")

    if isinstance(positions, list) and positions:
        titles = [p.get("title", "") for p in positions]
        scores = [p.get("match_score", 0) for p in positions]
        reasons = [p.get("recommendation_reason", "") or "" for p in positions]
        unique_titles = len(set(titles))
        non_empty_reasons = sum(1 for r in reasons if r.strip())
        print(f"  unique titles: {unique_titles}, non-empty reasons: {non_empty_reasons}")
        print(f"  scores: min={min(scores):.1f} max={max(scores):.1f} range={max(scores)-min(scores):.1f}")

        # Detail on first position
        pid = positions[0]["id"]
        r = requests.get(f"{BASE}/recommendation/positions/{pid}/detail", headers=H, timeout=120)
        detail = safe_json(r)
        if r.status_code == 200:
            ma = detail.get("match_analysis", {})
            overall = ma.get("overall_match_score")
            emb = detail.get("embedding_match_score")
            list_score = positions[0].get("match_score")
            print(f"  Detail: list={list_score} overall={overall} embedding={emb}")
            print(f"  gaps={len(ma.get('skill_gaps',[]))} strengths={len(ma.get('strength_points',[]))}")
            reason_preview = (ma.get('recommendation_reason', '') or '')[:80]
            print(f"  reason: {reason_preview}...")

        return {
            'edu': edu, 'k': k, 't': t, 'p': p,
            'score_range': f"{min(scores):.1f}-{max(scores):.1f}",
            'score_max': max(scores),
            'unique_titles': unique_titles,
            'non_empty_reasons': non_empty_reasons,
            'elapsed': elapsed,
        }
    return None

# ====== RUN BOTH TESTS ======
print("=" * 70)
print("MASTER STUDENT: PKU AI Master, PyTorch, CCF-A, ByteDance intern, ACM")
print("=" * 70)
master_desc = "北京大学人工智能专业硕士，精通PyTorch和TensorFlow深度学习框架，发表过2篇CCF-A论文，在字节跳动算法岗实习6个月，参加过ACM区域赛获得银牌，CET-6 580分"
master = run_test("MASTER", master_desc)

print()
print("=" * 70)
print("BACHELOR STUDENT: CS Bachelor, HTML/CSS/JS basics, blog project, CET-4")
print("=" * 70)
bachelor_desc = "本科学历，计算机科学与技术专业，学过HTML/CSS/JavaScript基础，会用Photoshop做简单切图，在学校做过一个简单的个人博客项目，CET-4 425分通过，无实习经验，无竞赛经历"
bachelor = run_test("BACHELOR", bachelor_desc)

# ====== COMPARISON ======
print()
print("=" * 70)
print("COMPARISON")
print("=" * 70)
if master and bachelor:
    print(f"{'Metric':<25} {'Master':>12} {'Bachelor':>12} {'Delta':>12}")
    print("-" * 60)
    print(f"{'knowledge_score':<25} {master['k']:>12} {bachelor['k']:>12} {bachelor['k']-master['k']:>+12}")
    print(f"{'tool_score':<25} {master['t']:>12} {bachelor['t']:>12} {bachelor['t']-master['t']:>+12}")
    print(f"{'project_score':<25} {master['p']:>12} {bachelor['p']:>12} {bachelor['p']-master['p']:>+12}")
    print(f"{'score_max':<25} {master['score_max']:>12.1f} {bachelor['score_max']:>12.1f}")
    print(f"{'unique_titles':<25} {master['unique_titles']:>12} {bachelor['unique_titles']:>12}")
    print(f"{'non-empty_reasons':<25} {master['non_empty_reasons']:>12} {bachelor['non_empty_reasons']:>12}")
    print(f"{'elapsed(s)':<25} {master['elapsed']:>12.1f} {bachelor['elapsed']:>12.1f}")

    print()
    if master['k'] < bachelor['k']:
        print("BUG CONFIRMED: knowledge_score: master < bachelor (should be opposite)")
    else:
        print("OK: knowledge_score: master >= bachelor")

    if master['p'] <= bachelor['p']:
        print("BUG CONFIRMED: project_score: master <= bachelor (should be higher)")
    else:
        print("OK: project_score: master > bachelor")

    if master['non_empty_reasons'] == 0:
        print("BUG CONFIRMED: recommendation_reason all empty")
    else:
        print("OK: recommendation_reason has content")
else:
    print("ERROR: Could not complete comparison")

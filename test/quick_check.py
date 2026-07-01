import requests, time

BASE = "http://127.0.0.1:8000/api/v1"

ts = str(int(time.time() * 1000))
r = requests.post(f'{BASE}/auth/register', json={
    'username': f'check_{ts[-6:]}', 'email': f'check_{ts[-6:]}@test.com', 'password': 'test1234'
})
token = r.json()['access_token']
H = {'Authorization': f'Bearer {token}'}

# MBTI
r = requests.get(f'{BASE}/personality/questions')
qs = r.json()['questions']
answers = {str(q['id']): 'A' for q in qs}
requests.post(f'{BASE}/personality/submit', json={'answers': answers}, headers=H)

# Ability with master description
desc = '北京大学人工智能专业硕士，精通PyTorch和TensorFlow深度学习框架，发表过2篇CCF-A论文，在字节跳动算法岗实习6个月，参加过ACM区域赛获得银牌，CET-6 580分'
print('Testing ability assessment...')
t0 = time.time()
r = requests.post(f'{BASE}/ability/describe', json={'text': desc}, headers=H, timeout=120)
elapsed = time.time() - t0
print(f'status={r.status_code} time={elapsed:.1f}s')
ability = r.json()
print(f'edu={ability.get("education")}')
print(f'k={ability.get("knowledge_score")} t={ability.get("tool_score")} p={ability.get("project_score")}')
print(f'certs={len(ability.get("certificates", []))}')
print(f'comps={len(ability.get("competitions", []))}')
raw = ability.get("raw_extracted_data", {})
print(f'raw skills: {raw.get("skills", []) if raw else "N/A"}')
print(f'raw projects: {[p.get("name") for p in raw.get("projects", [])] if raw else "N/A"}')

import requests, time

BASE = "http://127.0.0.1:8000/api/v1"

ts = str(int(time.time() * 1000))
r = requests.post(f'{BASE}/auth/register', json={
    'username': f'trend500_{ts[-6:]}', 'email': f'trend500_{ts[-6:]}@test.com', 'password': 'test1234'
})
token = r.json()['access_token']
H = {'Authorization': f'Bearer {token}'}

# Step 1: MBTI
r = requests.get(f'{BASE}/personality/questions')
qs = r.json()['questions']
answers = {str(q['id']): 'A' for q in qs}
requests.post(f'{BASE}/personality/submit', json={'answers': answers}, headers=H)

# Step 2: Ability
desc = '本科学历，计算机科学与技术专业，学过HTML/CSS/JavaScript基础，会用Photoshop做简单切图，在学校做过一个简单的个人博客项目，CET-4 425分通过，无实习经验，无竞赛经历'
requests.post(f'{BASE}/ability/describe', json={'text': desc}, headers=H, timeout=120)

# Step 3: Recommendation
requests.post(f'{BASE}/recommendation/recommend', json={'direction_id': 1}, headers=H, timeout=120)

# Step 4a: Trend - with error handling
print('Testing trend analysis...')
t0 = time.time()
r = requests.post(f'{BASE}/trend/analyze', json={'direction_id': 1, 'position_id': 0}, headers=H, timeout=120)
elapsed = time.time() - t0
print(f'status={r.status_code} time={elapsed:.1f}s')
print(f'Content-Type: {r.headers.get("content-type")}')
print(f'Response text (first 1000 chars):')
print(r.text[:1000])

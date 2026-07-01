"""直接调用 recommend 函数，验证编码速度"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
import sys
sys.path.insert(0, "backend")

import time
from app.database import engine
from sqlmodel import Session
from app.services.recommendation_service import recommend
from app.models.ability import AbilityPortrait
from app.models.user import User
from sqlmodel import select

with Session(engine) as session:
    # 找一个已做过能力评估的用户
    portrait = session.exec(select(AbilityPortrait).order_by(AbilityPortrait.id.desc())).first()
    if not portrait:
        print("无用户数据，先注册一个")
        sys.exit(1)
    user_id = portrait.user_id
    print(f"使用 user_id={user_id}")

    # 第一次调用（warm-up）
    print("\n=== 第一次调用 (warm-up) ===")
    t0 = time.time()
    result = recommend(session, user_id, 1)
    print(f"耗时: {time.time()-t0:.2f}s count={len(result)}")

    # 第二次调用
    print("\n=== 第二次调用 ===")
    t0 = time.time()
    result = recommend(session, user_id, 1)
    print(f"耗时: {time.time()-t0:.2f}s count={len(result)}")

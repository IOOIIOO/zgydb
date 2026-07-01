"""检查岗位文本长度对编码的影响 - 用tokenizer截断"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
import sys
sys.path.insert(0, "backend")

import time
from app.database import engine
from sqlmodel import Session, select
from app.models.position import Position
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-zh-v1.5")

with Session(engine) as session:
    positions = list(session.exec(
        select(Position).where(Position.direction_id == 1, Position.is_active == True)
    ).all())[:41]

    # 测试不同截断长度（手动截断字符）
    for trunc_len in [None, 200, 150, 100, 50]:
        texts = []
        for p in positions:
            text = f"{p.title}：{p.description or ''}"
            if trunc_len:
                text = text[:trunc_len]
            texts.append(text)

        t0 = time.time()
        embs = model.encode(texts, batch_size=32, normalize_embeddings=True)
        elapsed = time.time() - t0
        print(f"截断{trunc_len}字: {elapsed:.2f}s")

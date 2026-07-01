"""直接对比：app环境下 vs 独立脚本的编码速度"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
import sys
sys.path.insert(0, "backend")

import time
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA: {torch.cuda.is_available()}")

# 导入app模块（模拟后端环境）
print("\n=== 导入 app 模块 ===")
from app.config import settings
print(f"DEBUG={settings.DEBUG}")

from sentence_transformers import SentenceTransformer
import numpy as np

print("\n=== 加载模型 ===")
t0 = time.time()
model = SentenceTransformer("BAAI/bge-large-zh-v1.5")
print(f"加载: {time.time()-t0:.2f}s")
print(f"设备: {model.device}")

# 构造模拟数据
texts = [f"前端开发工程师{i}，需要React和TypeScript" for i in range(41)]

print("\n=== 第一次编码 ===")
t0 = time.time()
embs = model.encode(texts, batch_size=32, normalize_embeddings=True)
print(f"41条编码: {time.time()-t0:.2f}s")

print("\n=== 第二次编码 ===")
t0 = time.time()
embs = model.encode(texts, batch_size=32, normalize_embeddings=True)
print(f"41条编码: {time.time()-t0:.2f}s")

# 用真实岗位文本测试
print("\n=== 用真实岗位文本测试 ===")
from app.database import engine
from sqlmodel import Session, select
from app.models.position import Position

with Session(engine) as session:
    positions = list(session.exec(
        select(Position).where(Position.direction_id == 1, Position.is_active == True)
    ).all())
    print(f"岗位数: {len(positions)}")
    pos_texts = [f"{p.title}：{p.description or ''}" for p in positions[:41]]

    t0 = time.time()
    embs = model.encode(pos_texts, batch_size=32, normalize_embeddings=True)
    print(f"真实岗位41条编码: {time.time()-t0:.2f}s")

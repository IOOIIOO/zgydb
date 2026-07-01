"""检查 embedding 模型运行设备（离线模式）"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
import time
import torch
from sentence_transformers import SentenceTransformer

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")

print("\n=== 加载模型 ===")
t0 = time.time()
model = SentenceTransformer("BAAI/bge-large-zh-v1.5")
print(f"加载耗时: {time.time()-t0:.2f}s")
print(f"模型设备: {model.device}")

# 测试编码速度
print("\n=== 编码测试 ===")
texts = [f"测试文本{i}，前端开发工程师，需要掌握React和TypeScript" for i in range(41)]
t0 = time.time()
embs = model.encode(texts, batch_size=32, normalize_embeddings=True)
print(f"41条文本编码(batch=32): {time.time()-t0:.2f}s")

t0 = time.time()
embs = model.encode(texts, batch_size=8, normalize_embeddings=True)
print(f"41条文本编码(batch=8): {time.time()-t0:.2f}s")

t0 = time.time()
embs = model.encode(texts, batch_size=1, normalize_embeddings=True)
print(f"41条文本编码(batch=1): {time.time()-t0:.2f}s")

t0 = time.time()
embs = model.encode(texts[:5], batch_size=32, normalize_embeddings=True)
print(f"5条文本编码: {time.time()-t0:.2f}s")

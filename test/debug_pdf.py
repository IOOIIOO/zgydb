"""排查 PDF 简历解析"""
import sys
sys.path.insert(0, "backend")

PDF_PATH = r"d:\zgyd\简历2.pdf"

# 测试1: pypdf 能否提取文字
print("=== 测试1: pypdf 提取文字 ===")
try:
    from pypdf import PdfReader
    from io import BytesIO
    with open(PDF_PATH, "rb") as f:
        content = f.read()
    reader = PdfReader(BytesIO(content))
    print(f"页数: {len(reader.pages)}")
    text_parts = []
    for i, page in enumerate(reader.pages):
        t = page.extract_text()
        print(f"  第{i+1}页提取文字长度: {len(t) if t else 0}")
        if t:
            text_parts.append(t)
    full_text = "\n".join(text_parts)
    print(f"总文字长度: {len(full_text)}")
    if full_text.strip():
        print(f"前500字: {full_text[:500]}")
    else:
        print("!! pypdf 提取文字为空 - 这是 PDF 解析失败的原因")
except Exception as e:
    print(f"pypdf 异常: {type(e).__name__}: {e}")

# 测试2: 检查文件头
print("\n=== 测试2: 文件头 ===")
with open(PDF_PATH, "rb") as f:
    header = f.read(10)
print(f"文件头: {header}")
print(f"是PDF: {header[:4] == b'%PDF'}")

# 测试3: 调用 extract_from_pdf 看实际返回
print("\n=== 测试3: extract_from_pdf 返回 ===")
from app.services.real_models.bailian_llm import extract_from_pdf
with open(PDF_PATH, "rb") as f:
    content = f.read()
result = extract_from_pdf(content)
print(f"返回: {result}")
print(f"education: '{result.get('education','')}'")
print(f"skills: {result.get('skills',[])}")
print(f"certificates: {result.get('certificates',[])}")
print(f"projects: {result.get('projects',[])}")

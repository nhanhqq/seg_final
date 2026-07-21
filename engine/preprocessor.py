# -*- coding: utf-8 -*-
"""
Module 2a: Xử Lý Văn Bản & Tiền Xử Lý (Text Preprocessor)
- Tách từ tiếng Việt bằng thư viện underthesea.word_tokenize (format="text")
- Chuyển về chữ thường (lowercase) & chuẩn hóa dấu câu
- Loại bỏ từ dừng tiếng Việt (stopwords.txt)
- Bảo toàn các từ khóa kỹ thuật lập trình đặc thù (C++, C#, Node.js, Next.js, CI/CD, K8s, AI, JS...)
- Tích hợp Từ điển Đồng nghĩa / Viết tắt (Synonym Expansion Map) giúp truy vấn tự động nhận diện
  các từ khóa tương đương (ví dụ: js <-> javascript, ml <-> machine learning, csdl <-> cơ sở dữ liệu).
"""

import os
import sys
import io
import re

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from underthesea import word_tokenize
    HAS_UNDERTHESEA = True
except ImportError:
    HAS_UNDERTHESEA = False

STOPWORDS_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "stopwords.txt")

# Từ điển đồng nghĩa và viết tắt kỹ thuật CNTT (Synonym Expansion Map)
SYNONYM_MAP = {
    "js": ["javascript"],
    "javascript": ["js"],
    "ts": ["typescript"],
    "typescript": ["ts"],
    "py": ["python"],
    "python": ["py"],
    "ml": ["machine_learning", "machine learning", "học_máy"],
    "ai": ["trí_tuệ_nhân_tạo", "artificial intelligence", "deep_learning"],
    "cnn": ["convolutional neural network", "deep_learning"],
    "k8s": ["kubernetes"],
    "kubernetes": ["k8s"],
    "csdl": ["cơ_sở_dữ_liệu", "database", "db"],
    "db": ["database", "cơ_sở_dữ_liệu", "sql", "nosql"],
    "database": ["cơ_sở_dữ_liệu", "db"],
    "oop": ["lập_trình_hướng_đối_tượng", "object oriented programming"],
    "sql injection": ["sqli", "bảo_mật", "security"],
    "sqli": ["sql injection"],
    "xss": ["cross site scripting", "bảo_mật", "security"],
    "ci cd": ["devops", "github actions", "pipeline"],
    "iac": ["infrastructure as code", "terraform"]
}

class TextPreprocessor:
    def __init__(self, stopwords_path=STOPWORDS_PATH):
        self.stopwords = set()
        self.load_stopwords(stopwords_path)
        # Danh sách từ ngắn hoặc từ khóa kỹ thuật cần giữ lại không bị lọc
        self.whitelist_short_words = {
            "c", "r", "ai", "ml", "js", "ts", "go", "ui", "ux", "os", "ip", "it", 
            "db", "c++", "c#", "k8s", "sql", "api", "git", "web", "dom", "ssr", "csr"
        }

    def load_stopwords(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip().lower()
                    if w:
                        self.stopwords.add(w)
        else:
            # Fallback stopwords chuẩn tiếng Việt nếu file chưa tồn tại
            self.stopwords = {
                "và", "của", "là", "cho", "trong", "với", "những", "các", "một", "cách", 
                "khi", "này", "được", "có", "tại", "hoặc", "như", "thì", "bởi", "vào", 
                "ra", "lại", "nên", "rằng", "từ", "về", "đến", "đã", "đang", "sẽ", 
                "cũng", "hay", "rất", "nhiều", "chỉ", "đây", "đó", "kia", "nào", "ai", 
                "bị", "đoạn", "bài", "viết", "hướng", "dẫn", "chi", "tiết"
            }

    def clean_and_normalize(self, text):
        """Làm sạch văn bản, bảo toàn các từ khóa kỹ thuật trước khi tách từ"""
        if not text:
            return ""
        text = text.lower()
        # Chuẩn hóa bảo toàn C++, C# và CI/CD
        text = text.replace("c++", " cplusplus ")
        text = text.replace("c#", " csharp ")
        text = text.replace("ci/cd", " cicd ")
        text = text.replace("node.js", " nodejs ")
        text = text.replace("next.js", " nextjs ")
        # Loại bỏ ký tự đặc biệt giữ lại chữ cái, số, dấu gạch dưới và khoảng trắng
        text = re.sub(r"[^\w\s_]", " ", text)
        return text

    def restore_special_tokens(self, token):
        """Khôi phục các token đặc thù sau tách từ"""
        if token == "cplusplus":
            return "c++"
        if token == "csharp":
            return "c#"
        if token == "cicd":
            return "ci cd"
        return token

    def tokenize(self, text, remove_stopwords=True):
        """
        Tách từ và trả về danh sách token đã làm sạch.
        Sử dụng underthesea format='text' nối từ ghép bằng dấu gạch dưới (_).
        """
        if not text or not isinstance(text, str):
            return []

        cleaned = self.clean_and_normalize(text)

        if HAS_UNDERTHESEA:
            try:
                seg_text = word_tokenize(cleaned, format="text")
                tokens = seg_text.split()
            except Exception:
                tokens = cleaned.split()
        else:
            tokens = cleaned.split()

        result = []
        for t in tokens:
            t = self.restore_special_tokens(t.strip())
            if not t:
                continue
            # Lọc từ quá ngắn trừ khi nằm trong whitelist từ khóa kỹ thuật
            if len(t) < 2 and t not in self.whitelist_short_words:
                continue
            # Lọc chuỗi số quá dài
            if t.isdigit() and len(t) > 6:
                continue
            # Lọc stopwords
            if remove_stopwords and (t in self.stopwords or t.replace("_", " ") in self.stopwords):
                continue
            result.append(t)

        return result

    def tokenize_with_positions(self, text, remove_stopwords=True):
        """
        Trả về danh sách token cùng ánh xạ từ token sang danh sách chỉ số vị trí xuất hiện trong văn bản.
        """
        tokens = self.tokenize(text, remove_stopwords=remove_stopwords)
        positions = {}
        for idx, token in enumerate(tokens):
            if token not in positions:
                positions[token] = []
            positions[token].append(idx)
        return tokens, positions

    def expand_query(self, tokens):
        """
        Mở rộng từ khóa truy vấn với từ điển đồng nghĩa (Synonym Expansion).
        Trả về dictionary ánh xạ {token: trọng_số_mở_rộng}
        - Từ gốc: trọng số 1.0
        - Từ đồng nghĩa / viết tắt mở rộng: trọng số 0.75
        """
        expanded = {}
        for t in tokens:
            expanded[t] = max(expanded.get(t, 0.0), 1.0)
            # Kiểm tra trong từ điển đồng nghĩa
            clean_t = t.replace("_", " ")
            if clean_t in SYNONYM_MAP:
                for syn in SYNONYM_MAP[clean_t]:
                    syn_token = syn.replace(" ", "_") if HAS_UNDERTHESEA else syn
                    expanded[syn_token] = max(expanded.get(syn_token, 0.0), 0.75)
            elif t in SYNONYM_MAP:
                for syn in SYNONYM_MAP[t]:
                    syn_token = syn.replace(" ", "_") if HAS_UNDERTHESEA else syn
                    expanded[syn_token] = max(expanded.get(syn_token, 0.0), 0.75)
        return expanded

if __name__ == "__main__":
    pre = TextPreprocessor()
    sample = "Lập trình hướng đối tượng OOP trong C++ và Python là kiến thức cốt lõi cho lập trình viên."
    tokens, pos = pre.tokenize_with_positions(sample)
    print("Tokens:", tokens)
    print("Positions:", pos)
    print("Expanded:", pre.expand_query(tokens))


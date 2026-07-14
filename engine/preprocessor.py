# -*- coding: utf-8 -*-
"""
Module 2a: Xử Lý Văn Bản & Tiền Xử Lý (Text Preprocessor)
- Tách từ tiếng Việt bằng thư viện underthesea.word_tokenize
- Chuyển về chữ thường (lowercase)
- Loại bỏ từ dừng tiếng Việt (stopwords)
- Chuẩn hóa các từ khóa lập trình đặc thù (C++, C#, AI, JS, Git...)
- Ghi nhận vị trí xuất hiện của từ (positions) hỗ trợ highlight và tìm kiếm
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

STOPWORDS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed", "stopwords.txt")

class TextPreprocessor:
    def __init__(self, stopwords_path=STOPWORDS_PATH):
        self.stopwords = set()
        self.load_stopwords(stopwords_path)
        # Các từ khóa lập trình ngắn cần giữ lại không bị lọc theo độ dài
        self.whitelist_short_words = {"c", "r", "ai", "ml", "js", "go", "ui", "ux", "os", "ip", "it", "db", "c++", "c#"}

    def load_stopwords(self, path):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip().lower()
                    if w:
                        self.stopwords.add(w)
        else:
            # Fallback stopwords nếu chưa có file
            self.stopwords = {"và", "của", "là", "cho", "trong", "với", "những", "các", "một", "cách", "khi", "này", "được", "có", "tại", "hoặc", "như", "thì", "bởi", "vào", "ra", "lại", "nên"}

    def clean_and_normalize(self, text):
        """Làm sạch văn bản, bảo toàn các từ khóa như C++, C# trước khi tách từ"""
        if not text:
            return ""
        # Chuyển chữ thường
        text = text.lower()
        # Chuẩn hóa một số từ khóa c++, c#
        text = text.replace("c++", " cplusplus ")
        text = text.replace("c#", " csharp ")
        # Loại bỏ ký tự đặc biệt không mong muốn (giữ lại chữ cái, số, dấu gạch dưới, khoảng trắng)
        text = re.sub(r"[^\w\s_]", " ", text)
        return text

    def restore_special_tokens(self, token):
        """Khôi phục cplusplus -> c++, csharp -> c#"""
        if token == "cplusplus":
            return "c++"
        if token == "csharp":
            return "c#"
        return token

    def tokenize(self, text, remove_stopwords=True):
        """
        Tách từ và trả về danh sách các token đã được làm sạch.
        Nếu có underthesea, tách từ tiếng Việt chuẩn xác với format="text" (nối từ ghép bằng dấu _).
        """
        if not text or not isinstance(text, str):
            return []

        cleaned = self.clean_and_normalize(text)

        if HAS_UNDERTHESEA:
            try:
                # format="text" biến "lập trình hướng đối tượng" -> "lập_trình hướng_đối_tượng"
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
            # Lọc từ quá ngắn trừ khi trong whitelist
            if len(t) < 2 and t not in self.whitelist_short_words:
                continue
            # Lọc số đơn thuần dài hoặc ký tự rác
            if t.isdigit() and len(t) > 6:
                continue
            # Lọc stopwords
            if remove_stopwords and (t in self.stopwords or t.replace("_", " ") in self.stopwords):
                continue
            result.append(t)

        return result

    def tokenize_with_positions(self, text, remove_stopwords=True):
        """
        Trả về danh sách token và ánh xạ từ token sang danh sách vị trí xuất hiện (chỉ số từ/word index)
        Ví dụ: tokens = ['lập_trình', 'python', 'lập_trình'], positions = {'lập_trình': [0, 2], 'python': [1]}
        """
        tokens = self.tokenize(text, remove_stopwords=remove_stopwords)
        positions = {}
        for idx, token in enumerate(tokens):
            if token not in positions:
                positions[token] = []
            positions[token].append(idx)
        return tokens, positions

if __name__ == "__main__":
    pre = TextPreprocessor()
    sample = "Lập trình hướng đối tượng OOP trong C++ và Python là những kiến thức cơ bản cho người mới làm quen với công nghệ thông tin."
    tokens, pos = pre.tokenize_with_positions(sample)
    print("Tokens:", tokens)
    print("Positions:", pos)

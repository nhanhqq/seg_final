# -*- coding: utf-8 -*-
"""
Module 2b: Xây Dựng Chỉ Mục Ngược (Inverted Index Engine)
Cho Máy Tìm Kiếm Chuyên Sâu DevSeek (IT Learning Resources)
- Đọc dữ liệu từ data/raw/articles.json (hoặc devseek.db/articles.csv)
- Tách từ tiếng Việt chuyên nghiệp bằng TextPreprocessor cho các trường: title, tags, summary, content
- Xây dựng Inverted Index siêu tốc lưu trữ:
  + Danh sách tài liệu chứa từ khóa (Posting lists)
  + Tần suất từ trong tài liệu (TF - Term Frequency)
  + Vị trí xuất hiện của từ trong văn bản (Positions) hỗ trợ exact/proximity queries và highlight
  + Tần suất riêng cho từng trường (field_tf: title, tags, summary, content) phục vụ Multi-Field Ranking & Okapi BM25
- Lưu trữ toàn bộ metadata phong phú (category, difficulty, views, rating, reading_time_min) vào doc_store.json
- Tổng hợp chỉ số thống kê chiều dài văn bản (avg_doc_length, field_avg_lengths) vào index_metadata.json.
"""

import os
import sys
import io
import json
import math
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.preprocessor import TextPreprocessor

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc="", unit="", ncols=88):
        print(desc)
        return iterable

RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "articles.json")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
INDEX_PATH = os.path.join(PROCESSED_DIR, "index.json")
DOC_STORE_PATH = os.path.join(PROCESSED_DIR, "doc_store.json")
META_PATH = os.path.join(PROCESSED_DIR, "index_metadata.json")

class InvertedIndexer:
    def __init__(self, raw_path=RAW_PATH, processed_dir=PROCESSED_DIR):
        self.raw_path = raw_path
        self.processed_dir = processed_dir
        self.preprocessor = TextPreprocessor()
        
        # Cấu trúc Inverted Index:
        # { term: { doc_id: { "tf": int, "positions": list, "field_tf": {"title": int, "tags": int, "summary": int, "content": int} } } }
        self.inverted_index = defaultdict(dict)
        self.doc_store = {}
        self.doc_count = 0

    def build_index(self):
        print(f"[Indexer] Đang đọc dữ liệu thô từ: {self.raw_path}")
        if not os.path.exists(self.raw_path):
            raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {self.raw_path}. Hãy chạy crawler trước.")

        with open(self.raw_path, "r", encoding="utf-8") as f:
            articles = json.load(f)

        self.doc_count = len(articles)
        print(f"[Indexer] Bắt đầu xử lý NLP và xây dựng chỉ mục ngược cho {self.doc_count} bài viết...")

        total_title_len = 0
        total_tags_len = 0
        total_summary_len = 0
        total_content_len = 0
        doc_lengths = {}

        for doc in tqdm(articles, desc="[Indexer] NLP & Lập chỉ mục", unit="bài", ncols=88):
            doc_id = doc["doc_id"]
            title = doc.get("title", "")
            tags = doc.get("tags", [])
            tags_str = " ".join(tags) if isinstance(tags, list) else str(tags)
            summary = doc.get("summary", "")
            content = doc.get("content", "")

            # Tokenize riêng biệt cho từng trường để tính chính xác field_tf và độ dài
            title_tokens = self.preprocessor.tokenize(title)
            tags_tokens = self.preprocessor.tokenize(tags_str)
            summary_tokens = self.preprocessor.tokenize(summary)
            content_tokens = self.preprocessor.tokenize(content)

            # Đếm tần suất trong từng trường
            field_counts = {
                "title": defaultdict(int),
                "tags": defaultdict(int),
                "summary": defaultdict(int),
                "content": defaultdict(int)
            }
            for t in title_tokens:
                field_counts["title"][t] += 1
            for t in tags_tokens:
                field_counts["tags"][t] += 1
            for t in summary_tokens:
                field_counts["summary"][t] += 1
            for t in content_tokens:
                field_counts["content"][t] += 1

            # Tổng hợp chuỗi token của toàn tài liệu để ghi nhận vị trí chính xác (Positions)
            all_tokens = []
            all_tokens.extend(title_tokens)
            all_tokens.extend(tags_tokens)
            all_tokens.extend(summary_tokens)
            all_tokens.extend(content_tokens)

            term_positions = defaultdict(list)
            for idx, token in enumerate(all_tokens):
                term_positions[token].append(idx)

            doc_len = len(all_tokens)
            doc_lengths[doc_id] = doc_len
            total_title_len += len(title_tokens)
            total_tags_len += len(tags_tokens)
            total_summary_len += len(summary_tokens)
            total_content_len += len(content_tokens)

            # Lưu vào Document Store với đầy đủ thông tin metadata phong phú phục vụ Faceted Search
            self.doc_store[doc_id] = {
                "doc_id": doc_id,
                "url": doc.get("url", ""),
                "title": title,
                "author": doc.get("author", "Chuyên gia IT"),
                "publish_date": doc.get("publish_date", "2024-01-01"),
                "category": doc.get("category", "Thuật Toán & OOP"),
                "difficulty": doc.get("difficulty", "Cơ bản"),
                "reading_time_min": doc.get("reading_time_min", 8),
                "views": doc.get("views", 1500),
                "rating": doc.get("rating", 4.8),
                "tags": tags if isinstance(tags, list) else [tags],
                "summary": summary,
                "content": content,
                "total_tokens": doc_len,
                "length_title": len(title_tokens),
                "length_tags": len(tags_tokens),
                "length_summary": len(summary_tokens),
                "length_content": len(content_tokens)
            }

            # Cập nhật Inverted Index cho từng từ trong tài liệu
            for term, positions in term_positions.items():
                total_tf = len(positions)
                self.inverted_index[term][doc_id] = {
                    "tf": total_tf,
                    "positions": positions,
                    "field_tf": {
                        "title": field_counts["title"][term],
                        "tags": field_counts["tags"][term],
                        "summary": field_counts["summary"][term],
                        "content": field_counts["content"][term]
                    }
                }

        # Tạo Metadata cho Inverted Index giúp tính toán TF-IDF & Okapi BM25 siêu mượt
        avg_doc_length = sum(doc_lengths.values()) / max(1, self.doc_count)
        metadata = {
            "doc_count": self.doc_count,
            "vocab_size": len(self.inverted_index),
            "avg_doc_length": avg_doc_length,
            "doc_lengths": doc_lengths,
            "field_avg_lengths": {
                "title": total_title_len / max(1, self.doc_count),
                "tags": total_tags_len / max(1, self.doc_count),
                "summary": total_summary_len / max(1, self.doc_count),
                "content": total_content_len / max(1, self.doc_count)
            }
        }

        os.makedirs(self.processed_dir, exist_ok=True)

        print("[Indexer] Đang lưu chỉ mục và kho tài liệu ra ổ đĩa...")
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(self.inverted_index, f, ensure_ascii=False, indent=2)

        with open(DOC_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.doc_store, f, ensure_ascii=False, indent=2)

        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"[Indexer -> Hoàn tất] Vocabulary size: {len(self.inverted_index)} từ | Tổng số tài liệu: {self.doc_count} | Avg length: {avg_doc_length:.1f} tokens.")
        return self.inverted_index, self.doc_store, metadata

if __name__ == "__main__":
    indexer = InvertedIndexer()
    indexer.build_index()

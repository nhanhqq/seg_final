# -*- coding: utf-8 -*-
"""
Module 2b: Xây Dựng Chỉ Mục Ngược (Inverted Index Engine)
- Đọc dữ liệu từ data/raw/articles.json
- Sử dụng TextPreprocessor để tách từ cho các trường: title, tags, content
- Xây dựng Inverted Index lưu trữ:
  + Danh sách tài liệu chứa từ khóa (posting lists)
  + Tần suất từ trong tài liệu (TF - Term Frequency)
  + Vị trí xuất hiện của từ (positions)
  + Tần suất riêng cho từng trường (field_tf: title, tags, content) để phục vụ Multi-field Ranking
- Lưu chỉ mục ra data/processed/index.json và data/processed/doc_store.json
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

RAW_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "articles.json")
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
INDEX_PATH = os.path.join(PROCESSED_DIR, "index.json")
DOC_STORE_PATH = os.path.join(PROCESSED_DIR, "doc_store.json")
META_PATH = os.path.join(PROCESSED_DIR, "index_metadata.json")

class InvertedIndexer:
    def __init__(self, raw_path=RAW_PATH, processed_dir=PROCESSED_DIR):
        self.raw_path = raw_path
        self.processed_dir = processed_dir
        self.preprocessor = TextPreprocessor()
        
        # Cấu trúc Inverted Index:
        # { term: { doc_id: { "tf": int, "positions": list, "field_tf": {"title": int, "tags": int, "content": int} } } }
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
        print(f"[Indexer] Bắt đầu xây dựng chỉ mục cho {self.doc_count} bài viết IT...")

        for doc in articles:
            doc_id = doc["doc_id"]
            title = doc.get("title", "")
            tags = doc.get("tags", [])
            tags_str = " ".join(tags) if isinstance(tags, list) else str(tags)
            summary = doc.get("summary", "")
            content = doc.get("content", "")

            # Tokenize từng trường
            title_tokens = self.preprocessor.tokenize(title)
            tags_tokens = self.preprocessor.tokenize(tags_str)
            # Tóm tắt + nội dung gộp chung cho trường content để quét vị trí toàn diện
            content_tokens = self.preprocessor.tokenize(summary + " " + content)

            # Tính field frequency
            field_counts = {
                "title": defaultdict(int),
                "tags": defaultdict(int),
                "content": defaultdict(int)
            }
            for t in title_tokens:
                field_counts["title"][t] += 1
            for t in tags_tokens:
                field_counts["tags"][t] += 1
            for t in content_tokens:
                field_counts["content"][t] += 1

            # Tổng hợp toàn bộ token trong tài liệu và ghi nhận vị trí
            all_tokens = []
            all_tokens.extend(title_tokens)
            all_tokens.extend(tags_tokens)
            all_tokens.extend(content_tokens)

            term_positions = defaultdict(list)
            for idx, token in enumerate(all_tokens):
                term_positions[token].append(idx)

            # Lưu vào document store
            self.doc_store[doc_id] = {
                "doc_id": doc_id,
                "url": doc.get("url", ""),
                "title": title,
                "author": doc.get("author", "Unknown"),
                "publish_date": doc.get("publish_date", ""),
                "tags": tags if isinstance(tags, list) else [tags],
                "summary": summary,
                "content": content,
                "total_tokens": len(all_tokens),
                "length_title": len(title_tokens),
                "length_tags": len(tags_tokens),
                "length_content": len(content_tokens)
            }

            # Cập nhật Inverted Index
            for term, positions in term_positions.items():
                total_tf = len(positions)
                self.inverted_index[term][doc_id] = {
                    "tf": total_tf,
                    "positions": positions,
                    "field_tf": {
                        "title": field_counts["title"][term],
                        "tags": field_counts["tags"][term],
                        "content": field_counts["content"][term]
                    }
                }

        # Tạo metadata để hỗ trợ tính IDF siêu nhanh
        metadata = {
            "doc_count": self.doc_count,
            "vocab_size": len(self.inverted_index),
            "avg_doc_length": sum(d["total_tokens"] for d in self.doc_store.values()) / max(1, self.doc_count)
        }

        # Đảm bảo thư mục lưu tồn tại
        os.makedirs(self.processed_dir, exist_ok=True)

        print("[Indexer] Đang lưu chỉ mục ra ổ đĩa...")
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(self.inverted_index, f, ensure_ascii=False, indent=2)

        with open(DOC_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.doc_store, f, ensure_ascii=False, indent=2)

        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"[Indexer] Xây dựng chỉ mục hoàn tất! Vocabulary size: {len(self.inverted_index)} từ.")
        return self.inverted_index, self.doc_store, metadata

if __name__ == "__main__":
    indexer = InvertedIndexer()
    indexer.build_index()

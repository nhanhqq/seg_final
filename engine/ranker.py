# -*- coding: utf-8 -*-
"""
Module 3: Truy Vấn & Xếp Hạng Kết Quả (Query Processor & TF-IDF Ranker)
- Xử lý câu hỏi truy vấn của người dùng giống như quy trình xử lý dữ liệu (tách từ underthesea, loại stopwords).
- Tính điểm số độ liên quan giữa truy vấn và tài liệu bằng Multi-field TF-IDF.
- Áp dụng trọng số tùy chỉnh cho các trường quan trọng (Tiêu đề, Tags, Nội dung).
- Trả về danh sách tài liệu được xếp hạng kèm theo đoạn tóm tắt có highlight từ khóa (<mark>).
"""

import os
import sys
import io
import json
import math
import time
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.preprocessor import TextPreprocessor

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
INDEX_PATH = os.path.join(PROCESSED_DIR, "index.json")
DOC_STORE_PATH = os.path.join(PROCESSED_DIR, "doc_store.json")
META_PATH = os.path.join(PROCESSED_DIR, "index_metadata.json")

class TFIDFRanker:
    def __init__(self, index_path=INDEX_PATH, doc_store_path=DOC_STORE_PATH, meta_path=META_PATH):
        self.preprocessor = TextPreprocessor()
        self.inverted_index = {}
        self.doc_store = {}
        self.metadata = {"doc_count": 0, "avg_doc_length": 1.0}
        self.load_index(index_path, doc_store_path, meta_path)

        # Trọng số cho các trường quan trọng theo yêu cầu đồ án
        self.weights = {
            "title": 3.0,
            "tags": 2.5,
            "content": 1.0
        }

    def load_index(self, index_path, doc_store_path, meta_path):
        if os.path.exists(index_path) and os.path.exists(doc_store_path):
            with open(index_path, "r", encoding="utf-8") as f:
                self.inverted_index = json.load(f)
            with open(doc_store_path, "r", encoding="utf-8") as f:
                self.doc_store = json.load(f)
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
            else:
                self.metadata["doc_count"] = len(self.doc_store)
        else:
            print("[Ranker] Cảnh báo: Chưa tìm thấy chỉ mục. Vui lòng chạy indexer trước.")

    def compute_idf(self, term):
        """
        Tính điểm Inverse Document Frequency (IDF) của từ khóa theo công thức chuẩn lsmoothed IDF:
        IDF(t) = log( (N + 1) / (df(t) + 1) ) + 1
        """
        N = self.metadata.get("doc_count", len(self.doc_store))
        if N == 0:
            return 0.0
        df = len(self.inverted_index.get(term, {}))
        return math.log((N + 1) / (df + 1)) + 1.0

    def search(self, query, top_k=10, page=1):
        """
        Nhận truy vấn, xếp hạng tài liệu theo độ liên quan Multi-field TF-IDF và trả về danh sách kết quả.
        """
        start_time = time.time()
        # Xử lý truy vấn
        query_tokens = self.preprocessor.tokenize(query, remove_stopwords=True)
        if not query_tokens:
            return {
                "query": query,
                "query_tokens": [],
                "total_results": 0,
                "time_taken_ms": round((time.time() - start_time) * 1000, 2),
                "results": [],
                "page": page,
                "total_pages": 0
            }

        # Tính toán điểm số cho từng tài liệu chứa ít nhất 1 từ khóa truy vấn
        doc_scores = defaultdict(float)
        matched_terms_per_doc = defaultdict(set)

        for term in set(query_tokens):
            if term not in self.inverted_index:
                continue
            
            idf = self.compute_idf(term)
            postings = self.inverted_index[term]

            for doc_id, posting in postings.items():
                field_tf = posting.get("field_tf", {"title": 0, "tags": 0, "content": posting.get("tf", 0)})
                
                # Trọng số TF kết hợp các trường
                weighted_tf = (
                    self.weights["title"] * field_tf.get("title", 0) +
                    self.weights["tags"] * field_tf.get("tags", 0) +
                    self.weights["content"] * field_tf.get("content", 0)
                )

                # Chuẩn hóa theo độ dài tài liệu để công bằng giữa bài ngắn và bài dài (Sublinear TF scaling)
                if weighted_tf > 0:
                    tf_score = 1.0 + math.log(weighted_tf)
                else:
                    tf_score = 0.0

                score_term = tf_score * idf
                doc_scores[doc_id] += score_term
                matched_terms_per_doc[doc_id].add(term)

        # Sắp xếp kết quả theo điểm số giảm dần
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        total_results = len(sorted_docs)
        total_pages = math.ceil(total_results / top_k) if total_results > 0 else 0

        # Phân trang
        start_idx = (page - 1) * top_k
        end_idx = start_idx + top_k
        paged_docs = sorted_docs[start_idx:end_idx]

        results = []
        for doc_id, score in paged_docs:
            doc_info = self.doc_store.get(doc_id, {})
            # Tạo highlight snippet
            highlighted_summary, highlighted_title = self.create_highlighted_snippet(
                doc_info, matched_terms_per_doc[doc_id], query_tokens
            )

            results.append({
                "doc_id": doc_id,
                "title": highlighted_title,
                "raw_title": doc_info.get("title", ""),
                "url": doc_info.get("url", "#"),
                "author": doc_info.get("author", "Unknown"),
                "publish_date": doc_info.get("publish_date", ""),
                "tags": doc_info.get("tags", []),
                "summary": highlighted_summary,
                "raw_summary": doc_info.get("summary", ""),
                "score": round(score, 4),
                "matched_terms": list(matched_terms_per_doc[doc_id])
            })

        time_taken = round((time.time() - start_time) * 1000, 2)
        return {
            "query": query,
            "query_tokens": query_tokens,
            "total_results": total_results,
            "time_taken_ms": time_taken,
            "results": results,
            "page": page,
            "total_pages": total_pages
        }

    def create_highlighted_snippet(self, doc_info, matched_terms, query_tokens):
        """
        Highlight từ khóa xuất hiện trong tiêu đề và đoạn tóm tắt bằng thẻ <mark>
        """
        title = doc_info.get("title", "")
        summary = doc_info.get("summary", "")
        content = doc_info.get("content", "")

        # Nếu summary không đủ dài, trích xuất thêm từ content chỗ chứa từ khóa
        full_text = (summary + " " + content).strip()
        
        # Sắp xếp các từ khóa theo độ dài giảm dần để tránh highlight trùng lặp một phần của từ ngắn trong từ dài
        terms_to_highlight = sorted(list(matched_terms) + query_tokens, key=lambda x: len(x), reverse=True)
        unique_terms = []
        for t in terms_to_highlight:
            clean_t = t.replace("_", " ").strip()
            if clean_t and clean_t not in unique_terms:
                unique_terms.append(clean_t)

        # Highlight title
        high_title = title
        for t in unique_terms:
            # Tìm không phân biệt hoa thường và thay thế với <mark>
            import re
            pattern = re.compile(re.escape(t), re.IGNORECASE)
            high_title = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", high_title)

        # Highlight summary hoặc trích xuất đoạn xung quanh từ khóa đầu tiên
        best_snippet = summary if len(summary) > 60 else full_text[:300] + "..."
        # Tìm xem từ khóa có trong best_snippet không, nếu không tìm trong content đoạn có chứa từ khóa
        found_in_snippet = False
        for t in unique_terms:
            if re.search(re.escape(t), best_snippet, re.IGNORECASE):
                found_in_snippet = True
                break
        
        if not found_in_snippet and content:
            for t in unique_terms:
                match = re.search(re.escape(t), content, re.IGNORECASE)
                if match:
                    pos = match.start()
                    start_cut = max(0, pos - 80)
                    end_cut = min(len(content), pos + 220)
                    best_snippet = ("..." if start_cut > 0 else "") + content[start_cut:end_cut] + "..."
                    break

        high_summary = best_snippet
        for t in unique_terms:
            pattern = re.compile(re.escape(t), re.IGNORECASE)
            high_summary = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", high_summary)

        return high_summary, high_title

if __name__ == "__main__":
    ranker = TFIDFRanker()
    res = ranker.search("python cho người mới")
    print(f"Tìm thấy {res['total_results']} kết quả trong {res['time_taken_ms']} ms")
    for r in res["results"]:
        print(f"[{r['score']}] {r['raw_title']} - {r['url']}")

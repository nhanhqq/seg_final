# -*- coding: utf-8 -*-
"""
Module 3: Truy Vấn & Xếp Hạng Kết Quả (Advanced Query Processor & Dual Ranking Engine)
Cho Máy Tìm Kiếm Chuyên Sâu DevSeek (IT Learning Resources)
- Hỗ trợ cả 2 thuật toán xếp hạng chuẩn công nghiệp: Multi-Field TF-IDF và Okapi BM25F (k1=1.5, b=0.75), cùng chế độ Hybrid kết hợp.
- Tự động mở rộng truy vấn và đồng nghĩa (Query Expansion & Synonym Boosting) nhờ TextPreprocessor (js -> javascript, ml -> machine learning...).
- Hỗ trợ lọc theo khía cạnh (Faceted Filtering): Danh mục (Category), Độ khó (Difficulty).
- Hỗ trợ sắp xếp đa dạng (Sorting): Độ liên quan (Relevance), Mới nhất (Newest), Xem nhiều (Popularity), Điểm cao (Rating).
- Tạo đoạn tóm tắt động có highlight từ khóa (<mark>) thông minh không làm vỡ cấu trúc HTML.
"""

import os
import sys
import io
import json
import math
import time
import re
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.preprocessor import TextPreprocessor

PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
INDEX_PATH = os.path.join(PROCESSED_DIR, "index.json")
DOC_STORE_PATH = os.path.join(PROCESSED_DIR, "doc_store.json")
META_PATH = os.path.join(PROCESSED_DIR, "index_metadata.json")

class TFIDFRanker:
    """
    Dual Ranking Engine hỗ trợ Multi-Field TF-IDF, Okapi BM25 và Hybrid.
    Tên lớp giữ nguyên TFIDFRanker để tương thích hoàn toàn với các module khác.
    """
    def __init__(self, index_path=INDEX_PATH, doc_store_path=DOC_STORE_PATH, meta_path=META_PATH):
        self.preprocessor = TextPreprocessor()
        self.inverted_index = {}
        self.doc_store = {}
        self.metadata = {
            "doc_count": 0, 
            "avg_doc_length": 1.0, 
            "doc_lengths": {},
            "field_avg_lengths": {"title": 10.0, "tags": 5.0, "summary": 40.0, "content": 200.0}
        }
        self.load_index(index_path, doc_store_path, meta_path)

        # Trọng số ưu tiên cho các trường thông tin (Field weights)
        self.field_weights = {
            "title": 3.0,
            "tags": 2.5,
            "summary": 1.5,
            "content": 1.0
        }

        # Tham số chuẩn của Okapi BM25
        self.bm25_k1 = 1.5
        self.bm25_b = 0.75

    def load_index(self, index_path, doc_store_path, meta_path):
        if os.path.exists(index_path) and os.path.exists(doc_store_path):
            with open(index_path, "r", encoding="utf-8") as f:
                self.inverted_index = json.load(f)
            with open(doc_store_path, "r", encoding="utf-8") as f:
                self.doc_store = json.load(f)
            if os.path.exists(meta_path):
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.metadata.update(meta)
            else:
                self.metadata["doc_count"] = len(self.doc_store)
        else:
            print("[Ranker] Cảnh báo: Chưa tìm thấy chỉ mục. Vui lòng chạy indexer trước.")

    def compute_idf(self, term):
        """
        Tính điểm Inverse Document Frequency (IDF) smoothed:
        IDF(t) = log( (N + 1) / (df(t) + 1) ) + 1.0
        """
        N = self.metadata.get("doc_count", len(self.doc_store))
        if N == 0:
            return 0.0
        df = len(self.inverted_index.get(term, {}))
        return math.log((N + 1.0) / (df + 1.0)) + 1.0

    def compute_bm25_idf(self, term):
        """
        IDF chuẩn Okapi BM25:
        IDF_BM25(t) = log( (N - df + 0.5) / (df + 0.5) + 1 )
        """
        N = self.metadata.get("doc_count", len(self.doc_store))
        if N == 0:
            return 0.0
        df = len(self.inverted_index.get(term, {}))
        val = (N - df + 0.5) / (df + 0.5)
        return max(0.1, math.log(val + 1.0))

    def search(self, query, top_k=10, page=1, algorithm="tfidf", category=None, difficulty=None, sort_by="relevance"):
        """
        Thực hiện tìm kiếm, xếp hạng và lọc kết quả.
        - algorithm: "tfidf", "bm25", hoặc "hybrid"
        - category: bộ lọc theo chuyên đề ("Python", "JavaScript",...) hoặc None/All
        - difficulty: bộ lọc theo độ khó ("Cơ bản", "Trung bình", "Nâng cao") hoặc None/All
        - sort_by: "relevance", "newest", "popularity", "rating"
        """
        start_time = time.time()
        
        # 1. Tách từ truy vấn gốc
        query_tokens = self.preprocessor.tokenize(query, remove_stopwords=True)
        if not query_tokens:
            return self._empty_result(query, start_time, page)

        # 2. Mở rộng từ khóa (Query Expansion + Synonym Boosting)
        expanded_terms = self.preprocessor.expand_query(query_tokens)
        
        doc_scores_tfidf = defaultdict(float)
        doc_scores_bm25 = defaultdict(float)
        matched_terms_per_doc = defaultdict(set)

        doc_lengths = self.metadata.get("doc_lengths", {})
        avg_doc_length = self.metadata.get("avg_doc_length", 200.0)
        field_avg_lengths = self.metadata.get("field_avg_lengths", {"title": 10.0, "tags": 5.0, "summary": 40.0, "content": 200.0})

        # 3. Tính điểm độ liên quan cho từng tài liệu
        for term, boost_weight in expanded_terms.items():
            if term not in self.inverted_index:
                continue

            idf_tfidf = self.compute_idf(term)
            idf_bm25 = self.compute_bm25_idf(term)
            postings = self.inverted_index[term]

            for doc_id, posting in postings.items():
                field_tf = posting.get("field_tf", {"title": 0, "tags": 0, "summary": 0, "content": posting.get("tf", 0)})
                doc_info = self.doc_store.get(doc_id, {})

                # -- A. Tính Multi-Field TF-IDF --
                weighted_tf = (
                    self.field_weights["title"] * field_tf.get("title", 0) +
                    self.field_weights["tags"] * field_tf.get("tags", 0) +
                    self.field_weights["summary"] * field_tf.get("summary", 0) +
                    self.field_weights["content"] * field_tf.get("content", 0)
                )
                if weighted_tf > 0:
                    tf_score = 1.0 + math.log(weighted_tf)
                else:
                    tf_score = 0.0
                doc_scores_tfidf[doc_id] += tf_score * idf_tfidf * boost_weight

                # -- B. Tính Okapi BM25F --
                # Chuẩn hóa tần suất theo độ dài từng trường
                norm_field_tf = 0.0
                for f in ["title", "tags", "summary", "content"]:
                    f_tf = field_tf.get(f, 0)
                    if f_tf > 0:
                        f_val = doc_info.get(f, "")
                        if isinstance(f_val, list):
                            fallback_len = len(f_val)
                        elif isinstance(f_val, str):
                            fallback_len = len(f_val.split())
                        else:
                            fallback_len = 1
                        f_len = doc_info.get(f"length_{f}", fallback_len)
                        f_avg = field_avg_lengths.get(f, 20.0)
                        f_norm = f_tf / (1.0 - self.bm25_b + self.bm25_b * (f_len / max(1.0, f_avg)))
                        norm_field_tf += self.field_weights[f] * f_norm

                bm25_term_score = idf_bm25 * (norm_field_tf * (self.bm25_k1 + 1.0)) / (norm_field_tf + self.bm25_k1)
                doc_scores_bm25[doc_id] += bm25_term_score * boost_weight

                matched_terms_per_doc[doc_id].add(term)

        # 4. Tổng hợp điểm theo thuật toán lựa chọn
        doc_scores = {}
        all_doc_ids = set(doc_scores_tfidf.keys()).union(doc_scores_bm25.keys())

        if algorithm == "bm25":
            doc_scores = dict(doc_scores_bm25)
        elif algorithm == "hybrid":
            # Chuẩn hóa Max-Min rồi cộng trung bình
            max_t = max(doc_scores_tfidf.values()) if doc_scores_tfidf else 1.0
            max_b = max(doc_scores_bm25.values()) if doc_scores_bm25 else 1.0
            for d in all_doc_ids:
                s_t = doc_scores_tfidf.get(d, 0.0) / max(1e-5, max_t)
                s_b = doc_scores_bm25.get(d, 0.0) / max(1e-5, max_b)
                doc_scores[d] = 0.5 * s_t + 0.5 * s_b
        else:
            # Mặc định là Multi-Field TF-IDF
            doc_scores = dict(doc_scores_tfidf)

        # 5. Áp dụng Faceted Filtering (Lọc theo Category và Difficulty)
        filtered_docs = []
        available_categories = defaultdict(int)
        available_difficulties = defaultdict(int)

        for doc_id, score in doc_scores.items():
            doc_info = self.doc_store.get(doc_id, {})
            doc_cat = doc_info.get("category", "General")
            doc_diff = doc_info.get("difficulty", "Cơ bản")

            # Ghi nhận số lượng facet cho toàn bộ kết quả hợp lệ
            available_categories[doc_cat] += 1
            available_difficulties[doc_diff] += 1

            if category and category != "All" and doc_cat != category:
                continue
            if difficulty and difficulty != "All" and doc_diff != difficulty:
                continue

            filtered_docs.append((doc_id, score))

        # 6. Sắp xếp kết quả (Sorting)
        if sort_by == "newest":
            filtered_docs.sort(key=lambda x: self.doc_store.get(x[0], {}).get("publish_date", ""), reverse=True)
        elif sort_by == "popularity":
            filtered_docs.sort(key=lambda x: self.doc_store.get(x[0], {}).get("views", 0), reverse=True)
        elif sort_by == "rating":
            filtered_docs.sort(key=lambda x: self.doc_store.get(x[0], {}).get("rating", 0.0), reverse=True)
        else:
            # Mặc định sắp xếp theo điểm Relevance Score giảm dần
            filtered_docs.sort(key=lambda x: x[1], reverse=True)

        total_results = len(filtered_docs)
        total_pages = math.ceil(total_results / top_k) if total_results > 0 else 0

        # 7. Phân trang
        start_idx = (page - 1) * top_k
        end_idx = start_idx + top_k
        paged_docs = filtered_docs[start_idx:end_idx]

        results = []
        for doc_id, score in paged_docs:
            doc_info = self.doc_store.get(doc_id, {})
            high_summary, high_title = self.create_highlighted_snippet(
                doc_info, matched_terms_per_doc[doc_id], query_tokens
            )

            results.append({
                "doc_id": doc_id,
                "title": high_title,
                "raw_title": doc_info.get("title", ""),
                "url": doc_info.get("url", "#"),
                "author": doc_info.get("author", "Chuyên gia IT"),
                "publish_date": doc_info.get("publish_date", "2024-01-01"),
                "category": doc_info.get("category", "General"),
                "difficulty": doc_info.get("difficulty", "Cơ bản"),
                "reading_time_min": doc_info.get("reading_time_min", 6),
                "views": doc_info.get("views", 1000),
                "rating": doc_info.get("rating", 4.5),
                "tags": doc_info.get("tags", []),
                "summary": high_summary,
                "raw_summary": doc_info.get("summary", ""),
                "score": round(score, 4),
                "matched_terms": list(matched_terms_per_doc[doc_id])
            })

        time_taken = round((time.time() - start_time) * 1000, 2)
        return {
            "query": query,
            "query_tokens": query_tokens,
            "algorithm": algorithm.upper(),
            "total_results": total_results,
            "time_taken_ms": time_taken,
            "results": results,
            "page": page,
            "total_pages": total_pages,
            "facets": {
                "categories": dict(available_categories),
                "difficulties": dict(available_difficulties)
            }
        }

    def _empty_result(self, query, start_time, page):
        return {
            "query": query,
            "query_tokens": [],
            "algorithm": "TFIDF",
            "total_results": 0,
            "time_taken_ms": round((time.time() - start_time) * 1000, 2),
            "results": [],
            "page": page,
            "total_pages": 0,
            "facets": {"categories": {}, "difficulties": {}}
        }

    def create_highlighted_snippet(self, doc_info, matched_terms, query_tokens):
        """
        Highlight từ khóa xuất hiện trong tiêu đề và đoạn tóm tắt bằng thẻ <mark>
        """
        title = doc_info.get("title", "")
        summary = doc_info.get("summary", "")
        content = doc_info.get("content", "")

        full_text = (summary + " " + content).strip()
        
        terms_to_highlight = sorted(list(matched_terms) + query_tokens, key=lambda x: len(x), reverse=True)
        unique_terms = []
        for t in terms_to_highlight:
            clean_t = t.replace("_", " ").strip()
            if clean_t and len(clean_t) >= 2 and clean_t not in unique_terms:
                unique_terms.append(clean_t)

        # Highlight title
        high_title = title
        for t in unique_terms:
            pattern = re.compile(re.escape(t), re.IGNORECASE)
            high_title = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", high_title)

        # Highlight summary hoặc tìm đoạn văn xung quanh từ khóa trong content
        best_snippet = summary if len(summary) > 60 else full_text[:320] + "..."
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
                    start_cut = max(0, pos - 90)
                    end_cut = min(len(content), pos + 240)
                    best_snippet = ("..." if start_cut > 0 else "") + content[start_cut:end_cut] + "..."
                    break

        high_summary = best_snippet
        for t in unique_terms:
            pattern = re.compile(re.escape(t), re.IGNORECASE)
            high_summary = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", high_summary)

        return high_summary, high_title

if __name__ == "__main__":
    ranker = TFIDFRanker()
    res = ranker.search("python cho người mới", algorithm="bm25")
    print(f"Tìm thấy {res['total_results']} kết quả trong {res['time_taken_ms']} ms ({res['algorithm']})")
    for r in res["results"][:3]:
        print(f"[{r['score']}] {r['raw_title']} ({r['category']}) - {r['url']}")

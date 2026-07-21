# -*- coding: utf-8 -*-
"""
Script kiểm thử tự động toàn diện DevSeek (End-to-End Test Suite)
- Kiểm tra kết nối & cấu trúc dữ liệu SQLite (devseek.db, devseek_index.db)
- Kiểm tra hoạt động của Dual Ranker (TF-IDF vs BM25 vs Hybrid)
- Kiểm thử tự động toàn bộ endpoints của Giao diện Web Flask (via test_client)
- Đảm bảo 100% không lỗi trước khi demo hoặc nộp báo cáo.
"""

import os
import sys
import io
import json
import sqlite3
import unittest

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from web.app import app
from engine.ranker import TFIDFRanker

class TestDevSeekEndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.ranker = TFIDFRanker()

    def test_01_sqlite_databases(self):
        """Kiểm tra sự tồn tại và tính toàn vẹn của các database SQLite"""
        raw_db_path = os.path.join(PROJECT_ROOT, "data", "raw", "devseek.db")
        index_db_path = os.path.join(PROJECT_ROOT, "data", "processed", "devseek_index.db")
        
        self.assertTrue(os.path.exists(raw_db_path), "Chưa có devseek.db tại data/raw/")
        self.assertTrue(os.path.exists(index_db_path), "Chưa có devseek_index.db tại data/processed/")

        # Check raw db
        conn = sqlite3.connect(raw_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        raw_count = cursor.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(raw_count, 500, f"Số lượng bài viết trong raw db quá ít: {raw_count}")

        # Check index db
        conn = sqlite3.connect(index_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM inverted_index")
        posting_count = cursor.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(doc_count, 500, f"Số lượng documents trong index db: {doc_count}")
        self.assertGreaterEqual(posting_count, 1000, f"Số lượng postings trong index db: {posting_count}")

    def test_02_ranker_algorithms(self):
        """Kiểm tra hoạt động tìm kiếm với các thuật toán TF-IDF, BM25, HYBRID"""
        query = "python cho người mới"
        res_tfidf = self.ranker.search(query, algorithm="tfidf")
        self.assertGreater(res_tfidf["total_results"], 0, "TF-IDF không tìm thấy kết quả nào")
        self.assertEqual(res_tfidf["algorithm"], "TFIDF")

        res_bm25 = self.ranker.search(query, algorithm="bm25")
        self.assertGreater(res_bm25["total_results"], 0, "BM25 không tìm thấy kết quả nào")
        self.assertEqual(res_bm25["algorithm"], "BM25")

        res_hybrid = self.ranker.search(query, algorithm="hybrid")
        self.assertGreater(res_hybrid["total_results"], 0, "Hybrid không tìm thấy kết quả nào")
        self.assertEqual(res_hybrid["algorithm"], "HYBRID")

        # Kiểm tra highlight thẻ <mark> trong tóm tắt hoặc tiêu đề
        top_doc = res_tfidf["results"][0]
        self.assertTrue("<mark>" in top_doc["title"] or "<mark>" in top_doc["summary"], 
                        "Thẻ <mark> không xuất hiện trong highlight snippet")

    def test_03_flask_homepage(self):
        """Kiểm tra route trang chủ GET /"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DevSeek", response.data)
        self.assertIn(b"TF-IDF & BM25F", response.data)

    def test_04_flask_search_page(self):
        """Kiểm tra route tìm kiếm GET /search"""
        response = self.client.get("/search?q=docker&algorithm=bm25")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"docker", response.data.lower())
        self.assertIn(b"Okapi BM25F", response.data)

    def test_05_flask_annotate_page(self):
        """Kiểm tra route chấm điểm Ground Truth GET /annotate"""
        response = self.client.get("/annotate")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"q01", response.data)
        self.assertIn(b"Human Relevance Feedback", response.data)

    def test_06_flask_api_stats(self):
        """Kiểm tra REST API GET /api/stats"""
        response = self.client.get("/api/stats")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("doc_count", data)
        self.assertIn("vocab_size", data)
        self.assertGreaterEqual(data["doc_count"], 500)

    def test_07_flask_api_evaluate(self):
        """Kiểm tra REST API GET /api/evaluate"""
        response = self.client.get("/api/evaluate")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("summary", data)
        self.assertIn("automated_ground_truth", data["summary"])

    def test_08_flask_api_annotate(self):
        """Kiểm tra REST API POST /api/annotate"""
        payload = {
            "query_id": "test_q99",
            "query": "Kiểm thử API annotate",
            "approved_doc_ids": ["doc_python_001", "doc_python_002"]
        }
        response = self.client.post("/api/annotate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")

if __name__ == "__main__":
    print("="*80)
    print("DEVSEEK AUTOMATED TEST SUITE (DATABASE, ENGINE, WEB & API)")
    print("="*80)
    unittest.main(verbosity=2)

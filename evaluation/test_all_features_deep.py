# -*- coding: utf-8 -*-
"""
Script kiểm thử chuyên sâu toàn diện 100% các tính năng DevSeek (Deep Feature Verification Suite)
Đảm bảo mọi tổ hợp tham số, bộ lọc khía cạnh (facets), sắp xếp động, phân trang, mở rộng từ lóng (synonyms),
highlight từ khóa <mark>, và toàn bộ RESTful API đều hoạt động mượt mà không lỗi.
"""

import os
import sys
import io
import json
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
from engine.preprocessor import TextPreprocessor

class TestDevSeekDeepFeatures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.ranker = TFIDFRanker()
        cls.preprocessor = TextPreprocessor()

    def test_01_synonym_and_query_expansion(self):
        """Kiểm tra khả năng mở rộng từ viết tắt / từ đồng nghĩa IT (Synonym Boosting)"""
        # Test k8s -> kubernetes
        tokens_k8s = self.preprocessor.tokenize("hướng dẫn k8s")
        expanded_k8s = self.preprocessor.expand_query(tokens_k8s)
        self.assertIn("kubernetes", expanded_k8s, "Không mở rộng được 'k8s' sang 'kubernetes'")
        
        # Test csdl -> database
        tokens_csdl = self.preprocessor.tokenize("thiết kế csdl")
        expanded_csdl = self.preprocessor.expand_query(tokens_csdl)
        self.assertTrue("database" in expanded_csdl or "cơ_sở_dữ_liệu" in expanded_csdl, "Không mở rộng được 'csdl'")
        
        # Test js -> javascript
        tokens_js = self.preprocessor.tokenize("lập trình js")
        expanded_js = self.preprocessor.expand_query(tokens_js)
        self.assertIn("javascript", expanded_js, "Không mở rộng được 'js' sang 'javascript'")

        # Test search với từ viết tắt ra đúng tài liệu
        res_k8s = self.ranker.search("k8s", algorithm="bm25")
        self.assertGreater(res_k8s["total_results"], 0, "Tìm kiếm 'k8s' không ra kết quả nào")
        top_title = res_k8s["results"][0]["title"].lower() + res_k8s["results"][0]["summary"].lower()
        self.assertIn("kubernetes", top_title, "Kết quả top 1 của 'k8s' không chứa 'kubernetes'")

    def test_02_ranker_algorithms_comparative(self):
        """Kiểm tra so sánh giữa 3 thuật toán TF-IDF, Okapi BM25F và Hybrid"""
        query = "python cơ bản"
        res_tfidf = self.ranker.search(query, algorithm="tfidf")
        res_bm25 = self.ranker.search(query, algorithm="bm25")
        res_hybrid = self.ranker.search(query, algorithm="hybrid")

        self.assertEqual(res_tfidf["algorithm"], "TFIDF")
        self.assertEqual(res_bm25["algorithm"], "BM25")
        self.assertEqual(res_hybrid["algorithm"], "HYBRID")

        self.assertGreater(res_tfidf["total_results"], 0)
        self.assertGreater(res_bm25["total_results"], 0)
        self.assertGreater(res_hybrid["total_results"], 0)

        # Kiểm tra điểm số có được tính toán hợp lệ (số thực > 0)
        self.assertGreater(res_tfidf["results"][0]["score"], 0.0)
        self.assertGreater(res_bm25["results"][0]["score"], 0.0)
        self.assertGreater(res_hybrid["results"][0]["score"], 0.0)

    def test_03_faceted_filtering_category(self):
        """Kiểm tra lọc theo danh mục (Category Facet)"""
        category = "Web Development"
        res = self.ranker.search("python", category=category)
        for doc in res["results"]:
            self.assertEqual(doc["category"], category, f"Tài liệu trả về sai category: {doc['category']}")

        category_ds = "Data Science"
        res_ds = self.ranker.search("python", category=category_ds)
        for doc in res_ds["results"]:
            self.assertEqual(doc["category"], category_ds, f"Tài liệu trả về sai category: {doc['category']}")

    def test_04_faceted_filtering_difficulty(self):
        """Kiểm tra lọc theo độ khó (Difficulty Facet)"""
        diff = "Cơ bản"
        res = self.ranker.search("python", difficulty=diff)
        for doc in res["results"]:
            self.assertEqual(doc["difficulty"], diff, f"Tài liệu trả về sai difficulty: {doc['difficulty']}")

        diff_adv = "Nâng cao"
        res_adv = self.ranker.search("python", difficulty=diff_adv)
        for doc in res_adv["results"]:
            self.assertEqual(doc["difficulty"], diff_adv, f"Tài liệu trả về sai difficulty: {doc['difficulty']}")

    def test_05_combined_filtering(self):
        """Kiểm tra lọc kết hợp đồng thời Category + Difficulty"""
        cat = "Web Development"
        diff = "Cơ bản"
        res = self.ranker.search("python", category=cat, difficulty=diff)
        for doc in res["results"]:
            self.assertEqual(doc["category"], cat)
            self.assertEqual(doc["difficulty"], diff)

    def test_06_dynamic_sorting(self):
        """Kiểm tra các chế độ sắp xếp động: relevance, newest, popularity, rating"""
        query = "python"
        # 1. Relevance
        res_rel = self.ranker.search(query, sort_by="relevance")
        scores = [d["score"] for d in res_rel["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True), "Sắp xếp theo relevance bị sai thứ tự")

        # 2. Newest
        res_new = self.ranker.search(query, sort_by="newest")
        dates = [d["publish_date"] for d in res_new["results"]]
        self.assertEqual(dates, sorted(dates, reverse=True), "Sắp xếp theo newest bị sai thứ tự")

        # 3. Popularity
        res_pop = self.ranker.search(query, sort_by="popularity")
        views = [d["views"] for d in res_pop["results"]]
        self.assertEqual(views, sorted(views, reverse=True), "Sắp xếp theo popularity bị sai thứ tự")

        # 4. Rating
        res_rat = self.ranker.search(query, sort_by="rating")
        ratings = [d["rating"] for d in res_rat["results"]]
        self.assertEqual(ratings, sorted(ratings, reverse=True), "Sắp xếp theo rating bị sai thứ tự")

    def test_07_pagination_logic(self):
        """Kiểm tra phân trang (Pagination) và xử lý trang vượt giới hạn"""
        res_p1 = self.ranker.search("python", page=1, top_k=5)
        self.assertEqual(res_p1["page"], 1)
        self.assertLessEqual(len(res_p1["results"]), 5)

        if res_p1["total_pages"] >= 2:
            res_p2 = self.ranker.search("python", page=2, top_k=5)
            self.assertEqual(res_p2["page"], 2)
            # Kiểm tra tài liệu trang 1 và trang 2 không trùng lặp
            ids_p1 = {d["doc_id"] for d in res_p1["results"]}
            ids_p2 = {d["doc_id"] for d in res_p2["results"]}
            self.assertEqual(len(ids_p1.intersection(ids_p2)), 0, "Trang 1 và Trang 2 bị trùng ID tài liệu")

        # Test trang vượt giới hạn cực lớn (page=9999)
        res_huge = self.ranker.search("python", page=9999, top_k=5)
        self.assertIsInstance(res_huge["results"], list, "Trang vượt giới hạn không trả về danh sách")

    def test_08_highlight_tag_injection(self):
        """Kiểm tra chèn thẻ highlight <mark> và xử lý từ khóa ký tự đặc biệt"""
        doc_info = {
            "title": "Học lập trình C++ và Python cơ bản",
            "summary": "Hướng dẫn C++ và Python cơ bản cho người mới bắt đầu.",
            "content": "Nội dung chi tiết về C++ và Python cơ bản."
        }
        high_summary, high_title = self.ranker.create_highlighted_snippet(doc_info, {"python", "c++"}, ["python", "c++"])
        self.assertIn("<mark>", high_title.lower() + high_summary.lower(), "Không tạo được thẻ <mark> highlight")
        self.assertTrue("python" in high_summary.lower() or "c++" in high_title.lower())

    def test_09_web_ui_all_routes_and_combinations(self):
        """Kiểm tra các routes Flask UI với các tổ hợp tham số phức tạp"""
        # Homepage
        resp_home = self.client.get("/")
        self.assertEqual(resp_home.status_code, 200)

        # Search with BM25 + Facets + Sort + Page
        resp_search = self.client.get("/search?q=docker&algorithm=bm25&category=DevOps&difficulty=C%C6%A1+b%E1%BA%A3n&sort_by=rating&page=1")
        self.assertEqual(resp_search.status_code, 200)
        self.assertIn(b"docker", resp_search.data.lower())
        self.assertIn(b"Okapi BM25F", resp_search.data)

        # Annotate Portal
        resp_ann = self.client.get("/annotate")
        self.assertEqual(resp_ann.status_code, 200)
        self.assertIn(b"q01", resp_ann.data)

    def test_10_rest_api_schema_and_behavior(self):
        """Kiểm tra chi tiết schema và phản hồi của toàn bộ REST API endpoints"""
        # GET /api/search
        resp = self.client.get("/api/search?q=javascript&algorithm=hybrid&page=1")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn("total_results", data)
        self.assertIn("facets", data)
        self.assertIn("results", data)

        # GET /api/stats
        resp_stats = self.client.get("/api/stats")
        self.assertEqual(resp_stats.status_code, 200)
        stats_data = json.loads(resp_stats.data)
        self.assertIn("doc_count", stats_data)
        self.assertIn("vocab_size", stats_data)
        self.assertGreaterEqual(stats_data["doc_count"], 500)
        self.assertGreaterEqual(stats_data["vocab_size"], 900)

        # GET /api/evaluate
        resp_eval = self.client.get("/api/evaluate")
        self.assertEqual(resp_eval.status_code, 200)
        eval_data = json.loads(resp_eval.data)
        self.assertIn("summary", eval_data)

        # POST /api/annotate
        payload = {
            "query_id": "test_goal_deep",
            "query": "Kiểm thử sâu API annotate dưới /goal",
            "approved_doc_ids": ["doc_python_001", "doc_python_002"]
        }
        resp_post = self.client.post("/api/annotate", json=payload)
        self.assertEqual(resp_post.status_code, 200)
        post_data = json.loads(resp_post.data)
        self.assertEqual(post_data["status"], "success")

        # Kiểm tra file human_ground_truth.json đã được ghi đúng chưa
        gt_path = os.path.join(PROJECT_ROOT, "evaluation", "human_ground_truth.json")
        with open(gt_path, "r", encoding="utf-8") as f:
            gt_json = json.load(f)
        self.assertIn("test_goal_deep", gt_json)
        self.assertEqual(gt_json["test_goal_deep"]["ground_truth"], ["doc_python_001", "doc_python_002"])

if __name__ == "__main__":
    print("="*80)
    print("DEVSEEK DEEP FEATURE VERIFICATION SUITE (ALL COMBINATIONS & EDGE CASES)")
    print("="*80)
    unittest.main(verbosity=2)

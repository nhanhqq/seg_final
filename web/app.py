# -*- coding: utf-8 -*-
"""
Module 4: Giao Diện Web & RESTful API (Flask Web Application & Dual Ranking Controller)
Cho Máy Tìm Kiếm Chuyên Sâu DevSeek (IT Learning Resources)
- Phục vụ giao diện tìm kiếm hiện đại (Rich Aesthetics, Dark Mode, Glassmorphism, Dynamic Animations).
- API & Controller xử lý tìm kiếm với lựa chọn thuật toán: Multi-Field TF-IDF, Okapi BM25F, Hybrid.
- Hỗ trợ lọc theo chuyên đề (Category), độ khó (Difficulty) và sắp xếp (Sort By).
- API cung cấp số liệu thống kê và báo cáo đánh giá so sánh trực tiếp.
"""

import os
import sys
import io
import json
import math
from flask import Flask, render_template, request, jsonify

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.ranker import TFIDFRanker

app = Flask(__name__, template_folder="templates", static_folder="static")

# Khởi tạo Ranker toàn cục
ranker = None

def get_ranker():
    global ranker
    if ranker is None:
        ranker = TFIDFRanker()
    return ranker

@app.route("/")
def index():
    engine = get_ranker()
    doc_count = len(engine.doc_store)
    vocab_size = len(engine.inverted_index)
    return render_template("index.html", doc_count=doc_count, vocab_size=vocab_size)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    algorithm = request.args.get("algorithm", "tfidf").lower()
    category = request.args.get("category", "All")
    difficulty = request.args.get("difficulty", "All")
    sort_by = request.args.get("sort_by", "relevance")

    if page < 1:
        page = 1

    if not query:
        return render_template("index.html")

    engine = get_ranker()
    if not engine.inverted_index:
        engine.load_index(engine.INDEX_PATH, engine.DOC_STORE_PATH, engine.META_PATH)

    search_result = engine.search(
        query=query,
        top_k=10,
        page=page,
        algorithm=algorithm,
        category=category if category != "All" else None,
        difficulty=difficulty if difficulty != "All" else None,
        sort_by=sort_by
    )

    return render_template(
        "results.html",
        query=search_result["query"],
        query_tokens=search_result["query_tokens"],
        algorithm=search_result.get("algorithm", "TFIDF"),
        category=category,
        difficulty=difficulty,
        sort_by=sort_by,
        total_results=search_result["total_results"],
        time_taken_ms=search_result["time_taken_ms"],
        results=search_result["results"],
        current_page=search_result["page"],
        total_pages=search_result["total_pages"],
        facets=search_result.get("facets", {"categories": {}, "difficulties": {}})
    )

@app.route("/api/search")
def api_search():
    """API trả về JSON cho ứng dụng client hoặc đánh giá độc lập"""
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    algorithm = request.args.get("algorithm", "tfidf").lower()
    category = request.args.get("category", "All")
    difficulty = request.args.get("difficulty", "All")
    sort_by = request.args.get("sort_by", "relevance")

    engine = get_ranker()
    search_result = engine.search(
        query=query,
        top_k=10,
        page=page,
        algorithm=algorithm,
        category=category if category != "All" else None,
        difficulty=difficulty if difficulty != "All" else None,
        sort_by=sort_by
    )
    return jsonify(search_result)

@app.route("/api/stats")
def api_stats():
    """API trả về thống kê hệ thống toàn diện"""
    engine = get_ranker()
    return jsonify({
        "doc_count": len(engine.doc_store),
        "vocab_size": len(engine.inverted_index),
        "avg_doc_length": round(engine.metadata.get("avg_doc_length", 0), 2),
        "field_weights": getattr(engine, "field_weights", {"title": 3.0, "tags": 2.5, "summary": 1.5, "content": 1.0}),
        "bm25_params": {"k1": getattr(engine, "bm25_k1", 1.5), "b": getattr(engine, "bm25_b", 0.75)}
    })

@app.route("/api/evaluate")
def api_evaluate():
    """API trả về báo cáo đánh giá so sánh TF-IDF vs BM25 từ evaluation/eval_metrics.json"""
    eval_path = os.path.join(PROJECT_ROOT, "evaluation", "eval_metrics.json")
    if os.path.exists(eval_path):
        with open(eval_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Chưa có file đánh giá eval_metrics.json. Hãy chạy python main.py trước."}), 404

@app.route("/annotate")
def annotate_page():
    """Trang giao diện chấm điểm Ground Truth (Relevance Feedback)"""
    benchmark_path = os.path.join(PROJECT_ROOT, "evaluation", "benchmark_queries.json")
    queries = []
    if os.path.exists(benchmark_path):
        with open(benchmark_path, "r", encoding="utf-8") as f:
            queries = json.load(f)
    return render_template("annotate.html", queries=queries)

@app.route("/api/annotate", methods=["POST"])
def api_annotate():
    """API lưu trữ đánh giá Relevance (0/1) của chuyên gia vào human_ground_truth.json"""
    data = request.get_json() or {}
    query_id = data.get("query_id")
    query_text = data.get("query")
    approved_doc_ids = data.get("approved_doc_ids", [])

    if not query_id or not query_text:
        return jsonify({"error": "Thiếu thông tin query_id hoặc query"}), 400

    human_gt_path = os.path.join(PROJECT_ROOT, "evaluation", "human_ground_truth.json")
    gt_data = {}
    if os.path.exists(human_gt_path):
        try:
            with open(human_gt_path, "r", encoding="utf-8") as f:
                gt_data = json.load(f)
        except Exception:
            gt_data = {}

    gt_data[query_id] = {
        "query_id": query_id,
        "query": query_text,
        "ground_truth": approved_doc_ids,
        "annotation_type": "Human Web UI Annotated"
    }

    os.makedirs(os.path.dirname(human_gt_path), exist_ok=True)
    with open(human_gt_path, "w", encoding="utf-8") as f:
        json.dump(gt_data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "success", "message": f"Đã cập nhật Ground Truth cho {query_id}", "total_annotated": len(gt_data)})

if __name__ == "__main__":
    print("[Flask] Đang khởi động DevSeek Web Engine - Máy tìm kiếm Chuyên sâu IT...")
    app.run(host="0.0.0.0", port=5000, debug=True)

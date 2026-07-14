# -*- coding: utf-8 -*-
"""
Module 4: Giao Diện Web (Flask Web Application)
- Phục vụ giao diện tìm kiếm hiện đại (Rich Aesthetics, Dark Mode, Glassmorphism).
- API và Controller xử lý truy vấn tìm kiếm từ người dùng, tính toán thời gian, phân trang và hiển thị highlight.
"""

import os
import sys
import io
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

# Khởi tạo ranker
ranker = None

def get_ranker():
    global ranker
    if ranker is None:
        ranker = TFIDFRanker()
    return ranker

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1

    if not query:
        return render_template("index.html")

    engine = get_ranker()
    # Tải lại chỉ mục nếu vừa mới index xong mà ranker chưa cập nhật
    if not engine.inverted_index:
        engine.load_index(engine.INDEX_PATH, engine.DOC_STORE_PATH, engine.META_PATH)

    search_result = engine.search(query, top_k=10, page=page)
    
    return render_template(
        "results.html",
        query=search_result["query"],
        query_tokens=search_result["query_tokens"],
        total_results=search_result["total_results"],
        time_taken_ms=search_result["time_taken_ms"],
        results=search_result["results"],
        current_page=search_result["page"],
        total_pages=search_result["total_pages"]
    )

@app.route("/api/search")
def api_search():
    """API trả về JSON cho các ứng dụng client bên thứ ba hoặc đánh giá"""
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    engine = get_ranker()
    search_result = engine.search(query, top_k=10, page=page)
    return jsonify(search_result)

@app.route("/api/stats")
def api_stats():
    """API trả về thống kê hệ thống (tổng số tài liệu, từ vựng)"""
    engine = get_ranker()
    return jsonify({
        "doc_count": len(engine.doc_store),
        "vocab_size": len(engine.inverted_index),
        "weights": engine.weights
    })

if __name__ == "__main__":
    print("[Flask] Đang khởi động DevSeek - Máy tìm kiếm lập trình IT...")
    app.run(host="0.0.0.0", port=5000, debug=True)

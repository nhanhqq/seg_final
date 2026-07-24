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

@app.route("/react")
def react_app():
    return send_from_directory('static', 'index.html')

@app.route("/react/<path:subpath>")
def react_subpaths(subpath):
    return send_from_directory('static', 'index.html')

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
    # Ranker automatically loads index on init.

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

@app.route("/api/doc/<doc_id>")
def api_get_doc(doc_id):
    engine = get_ranker()
    doc_info = engine.doc_store.get(doc_id)
    if not doc_info and getattr(engine, "use_sqlite", False):
        subset = engine.sqlite_indexer.load_doc_store_subset([doc_id])
        if subset:
            doc_info = subset[doc_id]
            engine.doc_store[doc_id] = doc_info

    if doc_info:
        title = doc_info.get("title", "Document")
        author = doc_info.get("author", "Unknown")
        date = doc_info.get("publish_date", "Unknown")
        url = doc_info.get("url", "#")
        content = doc_info.get("content", "No content available.").replace("\n", "<br>")
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; color: #333; }}
                h1 {{ color: #2563eb; }}
                .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <div class="meta">
                Author: {author} | Date: {date} | <a href="{url}" target="_blank">Original Link</a>
            </div>
            <div class="content">
                {content}
            </div>
        </body>
        </html>
        """
        return html
    return "Document not found", 404

import requests
import re
from flask import Response

@app.route("/api/proxy")
def api_proxy():
    url = request.args.get("url")
    if not url:
        return "Missing URL", 400
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        content = resp.text

        # Inject <base> tag to fix relative links (css, js, images)
        base_tag = f'<base href="{url}">'
        if '<head>' in content:
            content = content.replace('<head>', f'<head>\n    {base_tag}', 1)
        else:
            content = re.sub(r'(<head[^>]*>)', rf'\1\n    {base_tag}', content, count=1, flags=re.IGNORECASE)

        # Strip security headers that prevent iframe embedding
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'x-frame-options', 'content-security-policy']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
                   
        return Response(content, resp.status_code, headers)
    except Exception as e:
        return f"Lỗi tải trang: {str(e)}", 500

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

from flask import send_from_directory

if __name__ == "__main__":
    print("[Flask] Đang khởi động DevSeek Web Engine - Máy tìm kiếm Chuyên sâu IT...")
    app.run(host="0.0.0.0", port=5000, debug=True)

# -*- coding: utf-8 -*-
"""
Tự động cập nhật tập benchmark queries & ground truth tương ứng với quy mô CSDL 520+ bài viết
"""

import os
import sys
import io
import json

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "articles.json")
BENCHMARK_PATH = os.path.join(PROJECT_ROOT, "evaluation", "benchmark_queries.json")

def generate_benchmark():
    if not os.path.exists(RAW_PATH):
        print("[Lỗi] Chưa có articles.json")
        return

    with open(RAW_PATH, "r", encoding="utf-8") as f:
        articles = json.load(f)

    # 20 câu truy vấn benchmark và từ khóa lọc tương ứng trong tags/title/summary
    query_definitions = [
        ("q01", "học python cơ bản cho người mới bắt đầu", ["python", "cơ bản", "người mới", "pandas", "fastapi"]),
        ("q02", "thuật toán sắp xếp nhanh quicksort bằng c++ và python", ["quicksort", "sắp xếp", "chia để trị"]),
        ("q03", "khái niệm lập trình hướng đối tượng oop và các tính chất", ["oop", "lập trình hướng đối tượng", "đóng gói", "kế thừa", "đa hình", "solid", "clean architecture"]),
        ("q04", "hiểu rõ về async await trong javascript và promise", ["async", "await", "promise", "callback", "bất đồng bộ"]),
        ("q05", "hướng dẫn sử dụng git branch và git merge khi làm việc nhóm", ["branch", "merge", "git", "github", "teamwork", "cơ bản"]),
        ("q06", "con trỏ pointer trong c++ và quản lý bộ nhớ động", ["pointer", "con trỏ", "bộ nhớ động", "linked list"]),
        ("q07", "kiến trúc restful api là gì nguyên tắc thiết kế chuẩn", ["restful api", "api", "gin", "fastapi", "backend", "http"]),
        ("q08", "docker là gì hướng dẫn dockerfile và docker compose", ["docker", "container", "kubernetes", "k8s", "devops"]),
        ("q09", "lệnh sql truy vấn select join group by cơ bản", ["sql", "select", "join", "group by", "database", "truy vấn"]),
        ("q10", "phân tích dữ liệu bằng pandas và numpy trong python", ["pandas", "numpy", "data science"]),
        ("q11", "xây dựng web api tốc độ cao với fastapi", ["fastapi", "web api"]),
        ("q12", "thuật toán học máy linear regression hồi quy tuyến tính", ["linear regression", "machine learning", "deep learning", "cnn"]),
        ("q13", "xử lý mảng nâng cao javascript với map filter reduce", ["map filter reduce", "array", "javascript"]),
        ("q14", "quản lý trạng thái ứng dụng redux toolkit trong react", ["redux", "state management", "react", "nextjs"]),
        ("q15", "hiểu rõ event loop và call stack trong nodejs", ["event loop", "call stack", "nodejs"]),
        ("q16", "cấu trúc dữ liệu danh sách liên kết đơn linked list", ["linked list", "cấu trúc dữ liệu", "con trỏ"]),
        ("q17", "thuật toán tìm kiếm nhị phân binary search c++", ["binary search", "tìm kiếm nhị phân", "thuật toán"]),
        ("q18", "lập trình đa luồng multithreading và goroutines", ["multithreading", "goroutines", "concurrency", "thread"]),
        ("q19", "sử dụng spring boot xây dựng microservices java", ["spring boot", "microservices", "java"]),
        ("q20", "bảo mật web phòng chống tấn công xss và sql injection", ["security", "xss", "sql injection", "bảo mật"])
    ]

    benchmark_queries = []
    for qid, query_text, keywords in query_definitions:
        matching_docs = []
        for doc in articles:
            doc_text = (doc.get("title", "") + " " + " ".join(doc.get("tags", [])) + " " + doc.get("summary", "")).lower()
            if any(kw.lower() in doc_text for kw in keywords):
                matching_docs.append(doc["doc_id"])
        
        benchmark_queries.append({
            "query_id": qid,
            "query": query_text,
            "ground_truth": matching_docs
        })

    with open(BENCHMARK_PATH, "w", encoding="utf-8") as f:
        json.dump(benchmark_queries, f, ensure_ascii=False, indent=2)

    print(f"[Generate Benchmark] Đã tạo tập benchmark cho 20 câu hỏi khớp với {len(articles)} bài viết tại: {BENCHMARK_PATH}")

if __name__ == "__main__":
    generate_benchmark()

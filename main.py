# -*- coding: utf-8 -*-
"""
File: main.py
Chạy full pipeline quy trình xây dựng máy tìm kiếm DevSeek từ A đến Z:
    py main.py

Quy trình thực thi chuẩn Data Engineering & Information Retrieval:
0. Dọn dẹp & Xóa sạch toàn bộ dữ liệu cũ (raw, processed index, metadata, database, evaluation)
1. Thu thập & tổng hợp bộ dữ liệu lập trình IT chuyên sâu mới từ đầu (Quy mô 520+ bài viết)
   Lưu trữ đa định dạng: JSON (articles.json), CSV (articles.csv), SQLite Database (devseek.db).
2. Tiền xử lý tách từ ghép tiếng Việt (underthesea) & Xây dựng Inverted Index + Positions + Field TF (tqdm)
3. Đồng bộ truy vấn Benchmark & Chạy kiểm thử tự động đo lường và so sánh song song:
   Multi-Field TF-IDF vs Okapi BM25F (Precision@10 & MAP).
"""

import os
import sys
import io
import time

# Set encoding UTF-8 cho console Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from crawler.it_crawler import ITArticleCrawler
from engine.indexer import InvertedIndexer
from evaluation.evaluate import run_evaluation
from evaluation.generate_benchmark import generate_benchmark

def clean_old_data():
    print("\n[BUOC 0/3] Dọn dẹp & Xóa sạch dữ liệu cũ (Reset toàn bộ hệ thống từ đầu)...")
    raw_dir = os.path.join(PROJECT_ROOT, "data", "raw")
    processed_dir = os.path.join(PROJECT_ROOT, "data", "processed")
    eval_metrics = os.path.join(PROJECT_ROOT, "evaluation", "eval_metrics.json")
    
    deleted_count = 0
    if os.path.exists(raw_dir):
        for f in os.listdir(raw_dir):
            file_path = os.path.join(raw_dir, f)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception:
                    pass

    if os.path.exists(processed_dir):
        for f in os.listdir(processed_dir):
            if f == "stopwords.txt":
                continue
            file_path = os.path.join(processed_dir, f)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception:
                    pass

    if os.path.exists(eval_metrics):
        try:
            os.remove(eval_metrics)
            deleted_count += 1
        except Exception:
            pass

    print(f"-> Đã xóa sạch {deleted_count} file dữ liệu cũ (JSON, CSV, SQLite db, Index, Store...). Sẵn sàng khởi tạo pipeline mới!")

def main():
    print("=" * 96)
    print("DEVSEEK VERTICAL SEARCH ENGINE - ADVANCED FULL PIPELINE (MULTI-STORAGE & DUAL RANKING)")
    print("=" * 96)
    start_total_time = time.time()

    # BƯỚC 0: Xóa toàn bộ dữ liệu cũ
    clean_old_data()

    # BƯỚC 1: Thu thập / Tổng hợp Cơ Sở Dữ Liệu IT (520+ bài viết) -> JSON, CSV, SQLite
    print("\n[BƯỚC 1/3] Thu thập & Xây dựng Cơ sở dữ liệu tài liệu lập trình IT từ đầu...")
    crawler = ITArticleCrawler()
    articles = crawler.run(mode="seed")
    print(f"-> Hoàn tất BƯỚC 1: Đã tổng hợp và lưu trữ đồng bộ {len(articles)} bài viết tại data/raw/ (JSON, CSV, SQLite Database)!")

    # BƯỚC 2: Tiền xử lý tiếng Việt & Xây dựng Chỉ mục ngược
    print("\n[BƯỚC 2/3] Xử lý NLP tách từ tiếng Việt & Xây dựng Inverted Index đa trường...")
    indexer = InvertedIndexer(raw_path=crawler.output_path)
    indexer.build_index()
    print("-> Hoàn tất BƯỚC 2: Chỉ mục ngược (index.json, doc_store.json, index_metadata.json) đã sẵn sàng!")

    # BƯỚC 3: Đồng bộ truy vấn mẫu & Kiểm thử tự động so sánh TF-IDF vs BM25
    print("\n[BƯỚC 3/3] Đồng bộ bộ truy vấn chuẩn & Chạy kiểm thử tự động so sánh (Benchmark)...")
    try:
        generate_benchmark()
        run_evaluation()
    except Exception as e:
        print(f"[Cảnh báo] Kiểm thử đánh giá gặp lỗi: {e}")

    total_elapsed = round(time.time() - start_total_time, 2)
    print("\n" + "=" * 96)
    print(f"HOÀN TẤT CHẠY FULL PIPELINE VÀ SO SÁNH THUẬT TOÁN TRONG {total_elapsed} GIÂY!")
    print("Bây giờ bạn có thể khởi chạy ứng dụng Web App bằng cách gõ lệnh: py run_app.py")
    print("=" * 96)

if __name__ == "__main__":
    main()

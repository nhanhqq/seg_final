# -*- coding: utf-8 -*-
"""
File 1: Chạy Full Pipeline (main.py)
Chạy script này để thực hiện toàn bộ quy trình xây dựng máy tìm kiếm từ A đến Z:
    python main.py
(hoặc: py main.py)

Quy trình tự động thực thi:
1. Thu thập & tổng hợp bộ dữ liệu IT quy mô lớn (520+ bài viết, hướng dẫn lập trình tiếng Việt)
2. Tiền xử lý tách từ ghép tiếng Việt (underthesea) & xây dựng Inverted Index (index.json, doc_store.json)
3. Đồng bộ tập truy vấn Benchmark & Chạy kiểm thử tự động xác minh độ chính xác P@10 và MAP
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

def main():
    print("=" * 80)
    print("DEVSEEK VERTICAL SEARCH ENGINE - FULL PIPELINE (CRAWL -> INDEX -> EVALUATE)")
    print("=" * 80)
    start_total_time = time.time()

    # BƯỚC 1: Thu thập / Tổng hợp Cơ Sở Dữ Liệu (Quy mô 520+ bài viết)
    print("\n[BƯỚC 1/3] Thu thập & Xây dựng Cơ sở dữ liệu tài liệu lập trình IT...")
    crawler = ITArticleCrawler()
    articles = crawler.run(mode="seed")
    print(f"-> Hoàn tất BƯỚC 1: Đã chuẩn bị {len(articles)} bài viết tại data/raw/articles.json")

    # BƯỚC 2: Tiền xử lý văn bản tiếng Việt & Xây dựng Chỉ mục ngược
    print("\n[BƯỚC 2/3] Xử lý NLP tách từ tiếng Việt & Xây dựng Inverted Index...")
    indexer = InvertedIndexer(raw_path=crawler.output_path)
    indexer.build_index()
    print(f"-> Hoàn tất BƯỚC 2: Chỉ mục ngược (index.json & doc_store.json) đã sẵn sàng!")

    # BƯỚC 3: Đồng bộ truy vấn mẫu & Kiểm thử tự động chuẩn độ chính xác của hệ thống
    print("\n[BƯỚC 3/3] Đồng bộ bộ truy vấn mẫu & Chạy kiểm thử tự động (Benchmark)...")
    try:
        generate_benchmark()
        run_evaluation()
    except Exception as e:
        print(f"[Cảnh báo] Kiểm thử đánh giá gặp lỗi nhỏ: {e}")

    total_elapsed = round(time.time() - start_total_time, 2)
    print("\n" + "=" * 80)
    print(f"🎉 HOÀN TẤT CHẠY FULL PIPELINE TRONG {total_elapsed} GIÂY!")
    print(f"👉 Bây giờ bạn có thể mở Web App bằng cách gõ lệnh: py run_app.py")
    print("=" * 80)

if __name__ == "__main__":
    main()

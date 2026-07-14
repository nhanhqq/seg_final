# -*- coding: utf-8 -*-
"""
File: main.py
Chạy full pipeline quy trình xây dựng máy tìm kiếm DevSeek từ A đến Z:
    py main.py

Quy trình thực thi:
0. Xóa sạch toàn bộ dữ liệu cũ (raw & processed index, metadata, evaluation)
1. Thu thập & tổng hợp bộ dữ liệu tài liệu lập trình IT mới từ đầu (520+ bài viết)
2. Tiền xử lý tách từ ghép tiếng Việt (underthesea) & Xây dựng Inverted Index (tqdm)
3. Đồng bộ truy vấn Benchmark & Chạy kiểm thử tự động đo lường P@10, MAP (tqdm)
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
    print("\n[BUOC 0/3] Don dep & Xoa sach du lieu cu (Reset he thong tu dau)...")
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

    print(f"-> Da xoa sach {deleted_count} file du lieu cu (articles.json, index.json, doc_store.json...). San sang xay dung moi!")

def main():
    print("=" * 80)
    print("DEVSEEK VERTICAL SEARCH ENGINE - FULL PIPELINE (CLEAN -> CRAWL -> INDEX -> EVAL)")
    print("=" * 80)
    start_total_time = time.time()

    # BUOC 0: Xoa toan bo du lieu cu
    clean_old_data()

    # BUOC 1: Thu thap / Tong hop Co So Du Lieu (Quy mo 520+ bai viet)
    print("\n[BUOC 1/3] Thu thap & Xay dung Co so du lieu tai lieu lap trinh IT tu dau...")
    crawler = ITArticleCrawler()
    articles = crawler.run(mode="seed")
    print(f"-> Hoan tat BUOC 1: Da chuan bi {len(articles)} bai viet moi tai data/raw/articles.json")

    # BUOC 2: Tien xu ly van ban tieng Viet & Xay dung Chi muc nguoc (co tqdm)
    print("\n[BUOC 2/3] Xu ly NLP tach tu tieng Viet & Xay dung Inverted Index...")
    indexer = InvertedIndexer(raw_path=crawler.output_path)
    indexer.build_index()
    print("-> Hoan tat BUOC 2: Chi muc nguoc (index.json & doc_store.json) da san sang!")

    # BUOC 3: Dong bo truy van mau & Kiem thu tu dong (co tqdm)
    print("\n[BUOC 3/3] Dong bo bo truy van mau & Chay kiem thu tu dong (Benchmark)...")
    try:
        generate_benchmark()
        run_evaluation()
    except Exception as e:
        print(f"[Canh bao] Kiem thu danh gia gap loi: {e}")

    total_elapsed = round(time.time() - start_total_time, 2)
    print("\n" + "=" * 80)
    print(f"HOAN TAT CHAY FULL PIPELINE VA XAY DUNG MOI TRONG {total_elapsed} GIAY!")
    print("Bay gio ban co the mo Web App bang cach go lenh: py run_app.py")
    print("=" * 80)

if __name__ == "__main__":
    main()

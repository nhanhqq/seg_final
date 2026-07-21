# -*- coding: utf-8 -*-
"""
Module 5b: Đánh Giá Hệ Thống & So Sánh Thuật Toán (Comparative Evaluation Suite)
Cho Máy Tìm Kiếm Chuyên Sâu DevSeek (IT Learning Resources)
- Đọc tập 20 truy vấn chuẩn và Ground Truth từ evaluation/benchmark_queries.json
- Thực hiện đánh giá song song 2 mô hình: Multi-Field TF-IDF vs Okapi BM25
- Tính toán Precision@10 (P@10) và MAP (Mean Average Precision) cho cả hai thuật toán
- Xuất bảng so sánh trực quan ra console và lưu đầy đủ số liệu vào evaluation/eval_metrics.json
"""

import os
import sys
import io
import json
import time

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.ranker import TFIDFRanker

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, desc="", unit="", ncols=88):
        print(desc)
        return iterable

BENCHMARK_PATH = os.path.join(PROJECT_ROOT, "evaluation", "benchmark_queries.json")
OUTPUT_METRICS_PATH = os.path.join(PROJECT_ROOT, "evaluation", "eval_metrics.json")

def calculate_precision_at_k(retrieved_ids, ground_truth_set, k=10):
    if k <= 0:
        return 0.0
    top_k = retrieved_ids[:k]
    hits = sum(1 for doc_id in top_k if doc_id in ground_truth_set)
    return round(hits / k, 4)

def calculate_average_precision(retrieved_ids, ground_truth_set):
    if not ground_truth_set:
        return 0.0
    
    hits = 0
    sum_precisions = 0.0
    for i, doc_id in enumerate(retrieved_ids):
        if doc_id in ground_truth_set:
            hits += 1
            precision_at_i = hits / (i + 1)
            sum_precisions += precision_at_i
            
    return round(sum_precisions / len(ground_truth_set), 4) if len(ground_truth_set) > 0 else 0.0

def run_evaluation():
    print("="*96)
    print("DEVSEEK VERTICAL SEARCH ENGINE - COMPARATIVE EVALUATION (TF-IDF vs BM25)")
    print("="*96)
    
    if not os.path.exists(BENCHMARK_PATH):
        raise FileNotFoundError(f"Không tìm thấy file benchmark: {BENCHMARK_PATH}. Hãy chạy generate_benchmark trước.")
        
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    ranker = TFIDFRanker()
    if not ranker.inverted_index:
        ranker.load_index(INDEX_PATH, DOC_STORE_PATH, META_PATH)

    results_detail = []
    total_p10_tfidf = 0.0
    total_ap_tfidf = 0.0
    total_time_tfidf = 0.0

    total_p10_bm25 = 0.0
    total_ap_bm25 = 0.0
    total_time_bm25 = 0.0

    for item in tqdm(benchmark, desc="[Evaluation] So sánh TF-IDF vs BM25", unit="câu", ncols=88):
        qid = item["query_id"]
        query = item["query"]
        gt_set = set(item["ground_truth"])

        # --- 1. Chạy đánh giá Multi-Field TF-IDF ---
        start_t = time.time()
        res_tfidf = ranker.search(query, top_k=50, page=1, algorithm="tfidf")
        elapsed_tfidf = round((time.time() - start_t) * 1000, 2)
        total_time_tfidf += elapsed_tfidf
        retrieved_tfidf = [r["doc_id"] for r in res_tfidf["results"]]

        p10_tfidf = calculate_precision_at_k(retrieved_tfidf, gt_set, k=10)
        ap_tfidf = calculate_average_precision(retrieved_tfidf, gt_set)
        total_p10_tfidf += p10_tfidf
        total_ap_tfidf += ap_tfidf

        # --- 2. Chạy đánh giá Okapi BM25 ---
        start_t = time.time()
        res_bm25 = ranker.search(query, top_k=50, page=1, algorithm="bm25")
        elapsed_bm25 = round((time.time() - start_t) * 1000, 2)
        total_time_bm25 += elapsed_bm25
        retrieved_bm25 = [r["doc_id"] for r in res_bm25["results"]]

        p10_bm25 = calculate_precision_at_k(retrieved_bm25, gt_set, k=10)
        ap_bm25 = calculate_average_precision(retrieved_bm25, gt_set)
        total_p10_bm25 += p10_bm25
        total_ap_bm25 += ap_bm25

        results_detail.append({
            "query_id": qid,
            "query": query,
            "ground_truth_count": len(gt_set),
            "tfidf": {
                "precision_at_10": p10_tfidf,
                "average_precision": ap_tfidf,
                "time_taken_ms": elapsed_tfidf
            },
            "bm25": {
                "precision_at_10": p10_bm25,
                "average_precision": ap_bm25,
                "time_taken_ms": elapsed_bm25
            }
        })

    print("\n" + "="*96)
    print(f"{'ID':<5} | {'Truy Vấn':<36} | {'P@10 (TFIDF)':<12} | {'P@10 (BM25)':<11} | {'AP (TFIDF)':<10} | {'AP (BM25)':<9}")
    print("-" * 96)
    for d in results_detail:
        q_display = (d["query"][:33] + "...") if len(d["query"]) > 36 else d["query"]
        t_info = d["tfidf"]
        b_info = d["bm25"]
        print(f"{d['query_id']:<5} | {q_display:<36} | {t_info['precision_at_10']:<12.4f} | {b_info['precision_at_10']:<11.4f} | {t_info['average_precision']:<10.4f} | {b_info['average_precision']:<9.4f}")

    num_queries = len(benchmark)
    mean_p10_tfidf = round(total_p10_tfidf / num_queries, 4)
    map_tfidf = round(total_ap_tfidf / num_queries, 4)
    avg_time_tfidf = round(total_time_tfidf / num_queries, 2)

    mean_p10_bm25 = round(total_p10_bm25 / num_queries, 4)
    map_bm25 = round(total_ap_bm25 / num_queries, 4)
    avg_time_bm25 = round(total_time_bm25 / num_queries, 2)

    print("-" * 96)
    print(f"TỔNG HỢP SO SÁNH ({num_queries} truy vấn):")
    print(f"  + [Multi-Field TF-IDF] Mean P@10: {mean_p10_tfidf:.4f} | MAP: {map_tfidf:.4f} | Thời gian TB: {avg_time_tfidf:.2f} ms")
    print(f"  + [Okapi BM25F]        Mean P@10: {mean_p10_bm25:.4f} | MAP: {map_bm25:.4f} | Thời gian TB: {avg_time_bm25:.2f} ms")
    print("="*96)

    eval_report = {
        "summary": {
            "num_queries": num_queries,
            "tfidf": {
                "mean_precision_at_10": mean_p10_tfidf,
                "mean_average_precision_MAP": map_tfidf,
                "avg_query_time_ms": avg_time_tfidf
            },
            "bm25": {
                "mean_precision_at_10": mean_p10_bm25,
                "mean_average_precision_MAP": map_bm25,
                "avg_query_time_ms": avg_time_bm25
            },
            "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "details": results_detail
    }

    os.makedirs(os.path.dirname(OUTPUT_METRICS_PATH), exist_ok=True)
    with open(OUTPUT_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, ensure_ascii=False, indent=2)

    print(f"[Evaluation] Đã xuất báo cáo số liệu so sánh chi tiết ra: {OUTPUT_METRICS_PATH}")
    return eval_report

if __name__ == "__main__":
    run_evaluation()

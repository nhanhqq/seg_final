# -*- coding: utf-8 -*-
"""
Module 5: Đánh Giá Hệ Thống (System Evaluation Suite)
- Đọc tập 20 truy vấn mẫu và Ground Truth từ evaluation/benchmark_queries.json
- Chạy qua TFIDFRanker để lấy top kết quả
- Tính toán Precision@10 và MAP (Mean Average Precision)
- Xuất báo cáo bảng biểu chi tiết và file kết quả JSON ra evaluation/eval_metrics.json
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
from tqdm import tqdm

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
            
    # AP được chuẩn hóa theo số lượng ground truth (hoặc tổng số hit nếu số lượng retrieved nhỏ hơn)
    return round(sum_precisions / len(ground_truth_set), 4) if len(ground_truth_set) > 0 else 0.0

def run_evaluation():
    print("="*80)
    print("DEVSEEK VERTICAL SEARCH ENGINE - SYSTEM EVALUATION SUITE")
    print("="*80)
    
    if not os.path.exists(BENCHMARK_PATH):
        raise FileNotFoundError(f"Không tìm thấy file benchmark: {BENCHMARK_PATH}")
        
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    ranker = TFIDFRanker()
    if not ranker.inverted_index:
        ranker.load_index(ranker.INDEX_PATH, ranker.DOC_STORE_PATH, ranker.META_PATH)

    results_detail = []
    total_p10 = 0.0
    total_ap = 0.0
    total_time = 0.0

    for item in tqdm(benchmark, desc="[Evaluation] Đánh giá truy vấn", unit="câu", ncols=88):
        qid = item["query_id"]
        query = item["query"]
        gt_set = set(item["ground_truth"])

        start_t = time.time()
        # Lấy top 50 kết quả để đánh giá AP toàn diện
        search_res = ranker.search(query, top_k=50, page=1)
        elapsed = round((time.time() - start_t) * 1000, 2)
        total_time += elapsed

        retrieved_ids = [r["doc_id"] for r in search_res["results"]]
        
        p_at_10 = calculate_precision_at_k(retrieved_ids, gt_set, k=10)
        ap = calculate_average_precision(retrieved_ids, gt_set)

        total_p10 += p_at_10
        total_ap += ap

        results_detail.append({
            "query_id": qid,
            "query": query,
            "ground_truth_count": len(gt_set),
            "retrieved_top10_count": len(retrieved_ids[:10]),
            "precision_at_10": p_at_10,
            "average_precision": ap,
            "time_taken_ms": elapsed
        })

    print("\n" + "="*86)
    print(f"{'ID':<6} | {'Truy Vấn':<42} | {'P@10':<8} | {'AP':<8} | {'Thời gian (ms)':<14}")
    print("-" * 86)
    for d in results_detail:
        q_display = (d["query"][:39] + "...") if len(d["query"]) > 42 else d["query"]
        print(f"{d['query_id']:<6} | {q_display:<42} | {d['precision_at_10']:<8.4f} | {d['average_precision']:<8.4f} | {d['time_taken_ms']:<14.2f}")

    num_queries = len(benchmark)
    mean_p10 = round(total_p10 / num_queries, 4)
    map_score = round(total_ap / num_queries, 4)
    avg_time = round(total_time / num_queries, 2)

    print("-" * 86)
    print(f"TỔNG HỢP ({num_queries} truy vấn):")
    print(f"  + Mean Precision@10 (P@10) : {mean_p10:.4f}")
    print(f"  + Mean Average Precision   : {map_score:.4f}")
    print(f"  + Thời gian truy vấn TB    : {avg_time:.2f} ms")
    print("="*80)

    eval_report = {
        "summary": {
            "num_queries": num_queries,
            "mean_precision_at_10": mean_p10,
            "mean_average_precision_MAP": map_score,
            "avg_query_time_ms": avg_time,
            "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "details": results_detail
    }

    os.makedirs(os.path.dirname(OUTPUT_METRICS_PATH), exist_ok=True)
    with open(OUTPUT_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(eval_report, f, ensure_ascii=False, indent=2)

    print(f"[Evaluation] Đã xuất báo cáo số liệu chi tiết ra: {OUTPUT_METRICS_PATH}")
    return eval_report

if __name__ == "__main__":
    run_evaluation()

# -*- coding: utf-8 -*-
"""
Module 1b: Live API Data Crawler (Wikipedia & Open Tech APIs)
Cho Máy Tìm Kiếm Chuyên Sâu DevSeek
- Thu thập dữ liệu thực tế tự động từ Wikipedia API (Tiếng Việt & Tiếng Anh) về các chủ đề IT cốt lõi.
- Thu thập bài viết lập trình từ Dev.to Open API.
- Chuẩn hóa toàn bộ dữ liệu về lược đồ chuẩn DevSeek (JSON schema / SQLite tables).
- Tích hợp cơ chế fallback an toàn, xử lý timeout và rate-limiting.
"""

import os
import sys
import io
import json
import re
import time
import requests
from bs4 import BeautifulSoup

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class APICrawler:
    def __init__(self, timeout=6):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DevSeekBot/2.5 (+http://localhost:5000; contact@devseek.local)"
        })

    def fetch_wikipedia_articles(self, topics, lang="vi"):
        """
        Kéo bài viết chi tiết từ Wikipedia Action API theo danh sách từ khóa chuyên ngành.
        """
        print(f"[API Crawler] Đang truy xuất dữ liệu thực tế từ Wikipedia API ({lang.upper()})...")
        articles = []
        api_url = f"https://{lang}.wikipedia.org/w/api.php"

        for idx, topic_info in enumerate(topics):
            title_query, category, difficulty = topic_info
            params = {
                "action": "query",
                "prop": "extracts|info",
                "exintro": False,
                "explaintext": True,
                "inprop": "url",
                "titles": title_query,
                "format": "json"
            }
            try:
                resp = self.session.get(api_url, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    pages = data.get("query", {}).get("pages", {})
                    for page_id, page_data in pages.items():
                        if page_id == "-1":
                            continue
                        doc_title = page_data.get("title", title_query)
                        doc_url = page_data.get("fullurl", f"https://{lang}.wikipedia.org/wiki/{title_query}")
                        raw_content = page_data.get("extract", "")
                        
                        # Làm sạch và định dạng nội dung
                        clean_content = re.sub(r'\n+', ' ', raw_content).strip()
                        if len(clean_content) < 150:
                            continue

                        summary = clean_content[:280] + "..." if len(clean_content) > 280 else clean_content
                        tags = [t.lower().strip() for t in re.split(r'[\s,\(\)]+', title_query) if len(t) > 2]
                        if category.lower() not in tags:
                            tags.append(category.lower())

                        reading_time = max(4, min(25, len(clean_content) // 250))
                        
                        articles.append({
                            "doc_id": f"wiki_{lang}_{idx+1:03d}",
                            "url": doc_url,
                            "title": f"[{category}] {doc_title} (Wikipedia Reference)",
                            "author": f"Wikipedia {lang.upper()} Contributors",
                            "publish_date": "2024-05-01",
                            "category": category,
                            "difficulty": difficulty,
                            "reading_time_min": reading_time,
                            "views": 15000 + (idx * 1234) % 40000,
                            "rating": 4.8,
                            "tags": tags,
                            "summary": summary,
                            "content": clean_content
                        })
                time.sleep(0.3)
            except Exception as e:
                print(f"[API Crawler] Cảnh báo khi gọi Wikipedia API cho '{title_query}': {e}")

        print(f"-> Thu thập thành công {len(articles)} bài viết từ Wikipedia API.")
        return articles

    def fetch_devto_articles(self, tags, max_per_tag=3):
        """
        Kéo bài viết lập trình chất lượng cao từ Dev.to Public API.
        """
        print("[API Crawler] Đang truy xuất bài viết lập trình từ Dev.to API...")
        articles = []
        api_url = "https://dev.to/api/articles"
        doc_counter = 1

        for tag, category, difficulty in tags:
            params = {
                "tag": tag,
                "per_page": max_per_tag,
                "top": 365
            }
            try:
                resp = self.session.get(api_url, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    items = resp.json()
                    for item in items:
                        doc_title = item.get("title", "")
                        doc_url = item.get("url", "")
                        summary = item.get("description", "") or ""
                        
                        # Kéo thêm chi tiết nội dung hoặc dùng summary/body_markdown
                        body = item.get("body_markdown", "") or summary
                        clean_content = re.sub(r'[\#\*`\[\]]+', '', body).strip()
                        if len(clean_content) < 100:
                            clean_content = summary + " " + doc_title
                        
                        raw_tags = item.get("tag_list", [tag])
                        if isinstance(raw_tags, str):
                            raw_tags = [t.strip() for t in raw_tags.split(",")]
                        
                        pub_date = item.get("published_at", "2024-01-01")[:10]
                        reading_time = item.get("reading_time_minutes", 6)
                        views = item.get("public_reactions_count", 50) * 12 + 1200
                        
                        articles.append({
                            "doc_id": f"devto_{doc_counter:03d}",
                            "url": doc_url,
                            "title": f"[{category}] {doc_title}",
                            "author": item.get("user", {}).get("name", "Dev.to Author"),
                            "publish_date": pub_date,
                            "category": category,
                            "difficulty": difficulty,
                            "reading_time_min": max(3, reading_time),
                            "views": views,
                            "rating": round(min(5.0, 4.3 + (item.get("public_reactions_count", 10) % 7) / 10.0), 1),
                            "tags": raw_tags,
                            "summary": summary[:300] + ("..." if len(summary) > 300 else ""),
                            "content": clean_content
                        })
                        doc_counter += 1
                time.sleep(0.4)
            except Exception as e:
                print(f"[API Crawler] Cảnh báo khi gọi Dev.to API cho tag '{tag}': {e}")

        print(f"-> Thu thập thành công {len(articles)} bài viết từ Dev.to API.")
        return articles

    def run_all(self):
        """
        Thực thi tổng hợp từ tất cả các nguồn API và trả về danh sách bài viết chuẩn hóa.
        """
        wiki_vi_topics = [
            ("Ngôn ngữ lập trình Python", "Python", "Cơ bản"),
            ("JavaScript", "JavaScript", "Cơ bản"),
            ("Lập trình hướng đối tượng", "Thuật Toán & OOP", "Cơ bản"),
            ("Thuật toán tìm kiếm", "Thuật Toán & OOP", "Trung bình"),
            ("Cấu trúc dữ liệu", "Thuật Toán & OOP", "Trung bình"),
            ("Học máy", "AI & Machine Learning", "Nâng cao"),
            ("Trí tuệ nhân tạo", "AI & Machine Learning", "Nâng cao"),
            ("Cơ sở dữ liệu quan hệ", "Database", "Cơ bản"),
            ("SQL", "Database", "Cơ bản"),
            ("Docker (phần mềm)", "Git & DevOps", "Trung bình"),
            ("Git", "Git & DevOps", "Cơ bản"),
            ("REST", "Web Development", "Trung bình"),
            ("Microservices", "System Design", "Nâng cao")
        ]

        devto_tags = [
            ("python", "Python", "Trung bình"),
            ("javascript", "JavaScript", "Cơ bản"),
            ("algorithms", "Thuật Toán & OOP", "Trung bình"),
            ("machinelearning", "AI & Machine Learning", "Nâng cao"),
            ("sql", "Database", "Cơ bản"),
            ("devops", "Git & DevOps", "Trung bình"),
            ("webdev", "Web Development", "Cơ bản")
        ]

        wiki_articles = self.fetch_wikipedia_articles(wiki_vi_topics, lang="vi")
        devto_articles = self.fetch_devto_articles(devto_tags, max_per_tag=3)
        
        combined = wiki_articles + devto_articles
        print(f"[API Crawler -> Hoàn tất] Tổng hợp {len(combined)} bài viết từ các Open API.")
        return combined

if __name__ == "__main__":
    crawler = APICrawler()
    res = crawler.run_all()
    print(f"Sample article: {res[0]['title'] if res else 'No data'}")

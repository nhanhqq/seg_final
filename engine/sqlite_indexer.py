# -*- coding: utf-8 -*-
"""
Module 2c: Relational SQLite Inverted Index Engine
Cho Máy Tìm Kiếm Chuyên Sâu DevSeek
- Lưu trữ toàn bộ Inverted Index, Document Store và Metadata vào cơ sở dữ liệu quan hệ SQLite (devseek_index.db).
- Tạo chỉ mục B-Tree (Indexes) trên cột `term` và `doc_id` giúp truy vấn siêu nhanh với độ phức tạp O(log V) thay vì load file JSON khổng lồ.
- Hỗ trợ tra cứu posting list, frequencies và positional data trực tiếp bằng câu lệnh SQL chuẩn.
"""

import os
import sys
import io
import json
import sqlite3

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
SQLITE_INDEX_PATH = os.path.join(PROCESSED_DIR, "devseek_index.db")

class SQLiteIndexer:
    def __init__(self, db_path=SQLITE_INDEX_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_to_sqlite(self, inverted_index, doc_store, metadata):
        """
        Ghi toàn bộ cấu trúc Inverted Index và Document Store vào devseek_index.db.
        """
        print(f"[SQLite Indexer] Đang khởi tạo và lưu Inverted Index ra SQLite DB: {self.db_path}...")
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1. Khởi tạo bảng documents
        cursor.execute("DROP TABLE IF EXISTS documents")
        cursor.execute("""
            CREATE TABLE documents (
                doc_id TEXT PRIMARY KEY,
                url TEXT,
                title TEXT,
                author TEXT,
                publish_date TEXT,
                category TEXT,
                difficulty TEXT,
                reading_time_min INTEGER,
                views INTEGER,
                rating REAL,
                tags TEXT,
                summary TEXT,
                content TEXT,
                total_tokens INTEGER,
                length_title INTEGER,
                length_tags INTEGER,
                length_summary INTEGER,
                length_content INTEGER
            )
        """)
        cursor.execute("CREATE INDEX idx_doc_cat ON documents(category)")
        cursor.execute("CREATE INDEX idx_doc_diff ON documents(difficulty)")

        # 2. Khởi tạo bảng inverted_index
        cursor.execute("DROP TABLE IF EXISTS inverted_index")
        cursor.execute("""
            CREATE TABLE inverted_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT,
                doc_id TEXT,
                tf INTEGER,
                positions TEXT,
                field_tf_title INTEGER,
                field_tf_tags INTEGER,
                field_tf_summary INTEGER,
                field_tf_content INTEGER
            )
        """)
        cursor.execute("CREATE INDEX idx_term ON inverted_index(term)")
        cursor.execute("CREATE INDEX idx_doc_id ON inverted_index(doc_id)")

        # 3. Khởi tạo bảng metadata
        cursor.execute("DROP TABLE IF EXISTS metadata")
        cursor.execute("""
            CREATE TABLE metadata (
                meta_key TEXT PRIMARY KEY,
                meta_value TEXT
            )
        """)

        # Insert Documents
        doc_rows = []
        for doc_id, info in doc_store.items():
            tags_str = json.dumps(info.get("tags", []), ensure_ascii=False) if isinstance(info.get("tags"), list) else str(info.get("tags", ""))
            doc_rows.append((
                doc_id,
                info.get("url", ""),
                info.get("title", ""),
                info.get("author", "Chuyên gia IT"),
                info.get("publish_date", "2024-01-01"),
                info.get("category", "General"),
                info.get("difficulty", "Cơ bản"),
                info.get("reading_time_min", 6),
                info.get("views", 1000),
                info.get("rating", 4.5),
                tags_str,
                info.get("summary", ""),
                info.get("content", ""),
                info.get("total_tokens", 0),
                info.get("length_title", 0),
                info.get("length_tags", 0),
                info.get("length_summary", 0),
                info.get("length_content", 0)
            ))
        cursor.executemany("""
            INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, doc_rows)

        # Insert Inverted Index Postings
        posting_rows = []
        for term, postings in inverted_index.items():
            for doc_id, posting in postings.items():
                positions_str = json.dumps(posting.get("positions", []))
                field_tf = posting.get("field_tf", {})
                posting_rows.append((
                    term,
                    doc_id,
                    posting.get("tf", 0),
                    positions_str,
                    field_tf.get("title", 0),
                    field_tf.get("tags", 0),
                    field_tf.get("summary", 0),
                    field_tf.get("content", 0)
                ))
                if len(posting_rows) >= 5000:
                    cursor.executemany("""
                        INSERT INTO inverted_index (term, doc_id, tf, positions, field_tf_title, field_tf_tags, field_tf_summary, field_tf_content)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, posting_rows)
                    posting_rows = []

        if posting_rows:
            cursor.executemany("""
                INSERT INTO inverted_index (term, doc_id, tf, positions, field_tf_title, field_tf_tags, field_tf_summary, field_tf_content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, posting_rows)

        # Insert Metadata
        for k, v in metadata.items():
            cursor.execute("INSERT INTO metadata VALUES (?, ?)", (k, json.dumps(v, ensure_ascii=False)))

        conn.commit()
        conn.close()
        print(f"[SQLite Indexer -> Hoàn tất] Đã lưu chỉ mục B-Tree siêu tốc vào devseek_index.db.")

    def load_postings_for_terms(self, terms):
        """
        Tra cứu posting lists trực tiếp từ SQLite cho tập từ khóa cho trước.
        """
        if not os.path.exists(self.db_path):
            return {}
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholders = ",".join(["?"] * len(terms))
        cursor.execute(f"""
            SELECT term, doc_id, tf, positions, field_tf_title, field_tf_tags, field_tf_summary, field_tf_content
            FROM inverted_index
            WHERE term IN ({placeholders})
        """, list(terms))

        results = {}
        for row in cursor.fetchall():
            t = row["term"]
            if t not in results:
                results[t] = {}
            results[t][row["doc_id"]] = {
                "tf": row["tf"],
                "positions": json.loads(row["positions"]) if row["positions"] else [],
                "field_tf": {
                    "title": row["field_tf_title"],
                    "tags": row["field_tf_tags"],
                    "summary": row["field_tf_summary"],
                    "content": row["field_tf_content"]
                }
            }
        conn.close()
        return results

    def load_doc_store_subset(self, doc_ids=None):
        """
        Load thông tin Document Store từ SQLite. Nếu doc_ids=None thì load toàn bộ.
        """
        if not os.path.exists(self.db_path):
            return {}
        conn = self.get_connection()
        cursor = conn.cursor()

        if doc_ids is not None and len(doc_ids) > 0:
            placeholders = ",".join(["?"] * len(doc_ids))
            cursor.execute(f"SELECT * FROM documents WHERE doc_id IN ({placeholders})", list(doc_ids))
        else:
            cursor.execute("SELECT * FROM documents")

        doc_store = {}
        for row in cursor.fetchall():
            d = dict(row)
            try:
                d["tags"] = json.loads(d["tags"])
            except Exception:
                d["tags"] = [t.strip() for t in d["tags"].split(",") if t.strip()] if isinstance(d["tags"], str) else []
            doc_store[d["doc_id"]] = d
        conn.close()
        return doc_store

    def load_metadata(self):
        if not os.path.exists(self.db_path):
            return {}
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM metadata")
        meta = {}
        for row in cursor.fetchall():
            meta[row["meta_key"]] = json.loads(row["meta_value"])
        conn.close()
        return meta

if __name__ == "__main__":
    indexer = SQLiteIndexer()
    print(f"SQLite Index path: {indexer.db_path}")

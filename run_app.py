# -*- coding: utf-8 -*-
"""
File 2: Khởi chạy Máy chủ Giao diện Web DevSeek (run_app.py)
Chạy script này để mở ứng dụng tìm kiếm trên trình duyệt:
    python run_app.py
Truy cập: http://localhost:5000
"""

import os
import sys
import io

# Set encoding UTF-8 cho console Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from web.app import app

def main():
    print("=" * 80)
    print("DEVSEEK VERTICAL SEARCH ENGINE - KHỞI CHẠY GIAO DIỆN WEB")
    print("[Web Server] May chu dang khoi dong tai: http://localhost:5000")
    print("[Instruction] Mo trinh duyet web va truy cap dia chi tren de tra cuu!")
    print("[Note] Nhan Ctrl + C de dung may chu.")
    print("=" * 80)
    
    # Khởi chạy Flask Web Server
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()

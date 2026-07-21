# DevSeek - Hệ Thống Tìm Kiếm Chuyên Sâu Dành Cho Lập Trình Viên (Vertical Search Engine)

## Giới thiệu chung
DevSeek là một máy tìm kiếm chuyên biệt (Vertical Search Engine) được xây dựng từ đầu (from scratch) dành riêng cho lĩnh vực Công nghệ thông tin (IT) và Lập trình. 

Hệ thống được thiết kế theo quy trình chuẩn của Data Engineering & Information Retrieval (Truy xuất thông tin), bao gồm các chức năng cốt lõi:
- **Thu thập dữ liệu tự động (Crawling)**: Thu thập và tổng hợp hàng trăm bài viết IT chuyên sâu và lưu trữ đa định dạng (JSON, CSV, SQLite Database).
- **Tiền xử lý & Lập chỉ mục (Indexing)**: Xử lý ngôn ngữ tự nhiên tiếng Việt (tách từ ghép với Underthesea), xây dựng cấu trúc dữ liệu Chỉ mục ngược (Inverted Index) đa trường kết hợp vị trí (Positions) và tần suất (Field TF).
- **Xếp hạng & Truy xuất (Ranking)**: Hỗ trợ hai thuật toán tìm kiếm và xếp hạng tài liệu phổ biến nhất là Multi-Field TF-IDF và Okapi BM25F.
- **Đánh giá tự động (Evaluation)**: Tích hợp hệ thống kiểm thử tự động, so sánh trực tiếp hiệu năng giữa TF-IDF và BM25 (đo lường bằng Precision@10 và MAP).
- **Giao diện Web (Web App)**: Giao diện trực quan cho phép người dùng tra cứu tài liệu dễ dàng, được xây dựng bằng Flask.

## Cài đặt môi trường
Đảm bảo bạn đã cài đặt Python (khuyến nghị phiên bản 3.8 trở lên).
Để cài đặt các thư viện cần thiết, hãy mở Terminal/Command Prompt tại thư mục dự án và chạy lệnh sau:

```bash
pip install -r requirements.txt
```

## Hướng dẫn sử dụng

Dự án bao gồm 2 quy trình chính: **Xây dựng dữ liệu & Đánh giá (Backend Pipeline)** và **Khởi chạy ứng dụng Web (Frontend App)**.

### Bước 1: Chạy Full Pipeline (Xây dựng dữ liệu, Lập chỉ mục & Kiểm thử)
Trước khi tìm kiếm, bạn cần chạy hệ thống để thu thập dữ liệu, tạo chỉ mục và đánh giá thuật toán.
Từ thư mục gốc của dự án, chạy file `main.py`:

```bash
python main.py
```

Quy trình sẽ tự động thực hiện tuần tự:
1. Xóa sạch dữ liệu cũ (reset toàn bộ hệ thống).
2. Thu thập bộ dữ liệu IT mới và lưu vào thư mục `data/raw/`.
3. Xử lý NLP tiếng Việt và tạo Inverted Index tại `data/processed/`.
4. Chạy kiểm thử benchmark tự động để so sánh thuật toán TF-IDF vs BM25.

### Bước 2: Khởi chạy Giao diện Tìm kiếm Web
Sau khi Bước 1 đã hoàn tất việc chuẩn bị dữ liệu, bạn có thể mở giao diện tìm kiếm dành cho người dùng cuối bằng cách chạy:

```bash
python run_app.py
```

Sau khi máy chủ khởi động thành công, hãy mở trình duyệt web và truy cập vào địa chỉ:
👉 **http://localhost:5000**

*(Lưu ý: Để dừng máy chủ web, bạn có thể nhấn tổ hợp phím `Ctrl + C` trên cửa sổ Terminal).*

## Cấu trúc thư mục dự án
- `crawler/`: Chứa các script crawl/thu thập dữ liệu từ các trang công nghệ.
- `data/`: Nơi lưu trữ dữ liệu thô (raw) và dữ liệu đã qua xử lý/lập chỉ mục (processed).
- `engine/`: Chứa core logic của máy tìm kiếm (Inverted Indexer, Retrieval/Ranking Models).
- `evaluation/`: Scripts kiểm thử tự động, sinh bộ truy vấn benchmark đánh giá hệ thống.
- `web/`: Mã nguồn Flask Backend và HTML/CSS/JS Frontend của ứng dụng web.
- `main.py`: Script kích hoạt toàn bộ quy trình Data pipeline & Evaluation.
- `run_app.py`: Script khởi chạy máy chủ Flask Web App.

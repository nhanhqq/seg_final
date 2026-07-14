@echo off
chcp 65001 > nul
echo ======================================================================
echo ĐANG TỰ ĐỘNG CÀO / XÂY DỰNG CƠ SỞ DỮ LIỆU & LẬP CHỈ MỤC NGƯỢC DEVSEEK...
echo ======================================================================
python build_db.py
echo.
pause

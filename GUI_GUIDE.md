# 🎯 Hướng dẫn sử dụng GUI WooCommerce Scraper

## Khởi chạy GUI

```bash
python gui.py
```

## Giao diện chính

### 🌐 Phần URL và Cài đặt cơ bản
- **URL WooCommerce**: Nhập URL của shop WooCommerce cần scrape
- **Nút "✓ Kiểm tra"**: Kiểm tra xem URL có hợp lệ và truy cập được không
- **URL mẫu**: Các nút nhanh để thử với URL demo

### ⚙️ Phần Tùy chọn Scraping
- **Số trang tối đa**: Số trang tối đa sẽ scrape (1-100)
- **Delay (giây)**: Thời gian nghỉ giữa các request (0.1-10.0 giây)
- **🔒 Sử dụng Proxy**: Bật/tắt proxy (khuyến nghị bật)

### 💾 Phần Xuất dữ liệu
- **📄 JSON**: Xuất dữ liệu ra file JSON
- **📊 CSV**: Xuất dữ liệu ra file CSV  
- **Thư mục lưu**: Chọn thư mục để lưu files

### 🎮 Phần Điều khiển
- **🚀 Bắt đầu Scraping**: Bắt đầu quá trình scraping
- **⏹️ Dừng**: Dừng scraping (chỉ hoạt động khi đang scrape)
- **🧹 Xóa Log**: Xóa log hiện tại

### 📊 Phần Progress và Log
- **Progress Bar**: Hiển thị trạng thái scraping
- **Log Area**: Hiển thị chi tiết quá trình scraping real-time
- **Status Bar**: Trạng thái hiện tại

## Quy trình sử dụng

### Bước 1: Nhập URL
1. Nhập URL WooCommerce vào ô "URL WooCommerce"
2. Bấm "✓ Kiểm tra" để kiểm tra URL
3. Hoặc dùng nút "URL mẫu" để thử nhanh

### Bước 2: Cài đặt tùy chọn
1. Chọn số trang tối đa muốn scrape
2. Điều chỉnh delay nếu cần (khuyến nghị 1.0-2.0 giây)
3. Giữ nguyên "Sử dụng Proxy" được bật

### Bước 3: Chọn định dạng xuất
1. Chọn JSON và/hoặc CSV
2. Chọn thư mục lưu file (mặc định: thư mục hiện tại)

### Bước 4: Bắt đầu scraping
1. Bấm "🚀 Bắt đầu Scraping"
2. Theo dõi log để xem tiến trình
3. Đợi hoàn thành hoặc bấm "⏹️ Dừng" nếu cần

## Các tính năng đặc biệt

### 📊 Log Real-time
- Hiển thị từng bước scraping
- Emoji và màu sắc dễ đọc
- Timestamp cho mỗi thao tác
- Thống kê chi tiết

### 🔧 Threading
- GUI không bị đơ khi scraping
- Có thể dừng scraping bất cứ lúc nào
- Xử lý lỗi an toàn

### 💾 Auto-naming
- Files được tự động đặt tên với timestamp
- Định dạng: `products_YYYYMMDD_HHMMSS.json/csv`
- Không lo ghi đè file cũ

## Xử lý lỗi thường gặp

### ❌ "Không thể import scraper.py"
- Đảm bảo file `scraper.py` có trong cùng thư mục
- Kiểm tra file `scraper.py` không bị lỗi syntax

### ❌ "Không tìm thấy sản phẩm nào"
- Kiểm tra URL có đúng là trang shop không
- Website có thể dùng cấu trúc HTML khác
- Thử với delay cao hơn (2-3 giây)

### ❌ "Không thể kết nối đến URL"
- Kiểm tra kết nối internet
- URL có thể bị chặn hoặc không tồn tại
- Thử tắt proxy nếu có vấn đề

## Tips sử dụng hiệu quả

### 🚀 Performance
- Bắt đầu với 1-2 trang để test
- Tăng delay nếu website chậm
- Dùng proxy để tránh bị block

### 📊 Data Quality
- Kiểm tra log để đảm bảo scrape đúng
- Xem mẫu sản phẩm trong log
- Check thống kê coverage

### 🔧 Troubleshooting
- Copy log để debug nếu có lỗi
- Thử với URL khác để so sánh
- Sử dụng "Kiểm tra URL" trước khi scrape

## Keyboard Shortcuts

- **Ctrl+C**: Copy text từ log
- **Ctrl+A**: Select all text trong log
- **F5**: Refresh (có thể cần restart app)

## Lưu ý quan trọng

⚠️ **Sử dụng có trách nhiệm:**
- Respect robots.txt của website
- Không spam quá nhiều request  
- Tuân thủ terms of service
- Chỉ scrape dữ liệu công khai

🔒 **Bảo mật:**
- Proxy được cấu hình sẵn
- Không lưu thông tin nhạy cảm
- Log được lưu local

📈 **Performance:**
- Tối ưu cho các shop WooCommerce phổ biến
- Hỗ trợ pagination tự động
- Retry mechanism cho các lỗi network 
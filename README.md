# 🛒 Enhanced WooCommerce Product Scraper

**Công cụ scraping sản phẩm WooCommerce mạnh mẽ với giao diện đồ họa và tính năng scraping chi tiết**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![WooCommerce](https://img.shields.io/badge/WooCommerce-Compatible-purple.svg)](https://woocommerce.com/)

## 📋 Mục lục
- [Tính năng chính](#-tính-năng-chính)
- [Cài đặt](#-cài-đặt)
- [Cách sử dụng](#-cách-sử-dụng)
- [Cấu hình](#-cấu-hình)
- [Dữ liệu thu thập](#-dữ-liệu-thu-thập)
- [Ví dụ](#-ví-dụ)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)

## 🚀 Tính năng chính

### 🎨 **Giao diện đồ họa (GUI)**
- Interface thân thiện, dễ sử dụng
- Real-time progress tracking và logging
- Tùy chọn scraping trực quan
- URL templates có sẵn
- Export đa định dạng (JSON/CSV)

### 🔍 **Scraping thông minh**
- **Scraping cơ bản**: Nhanh, lấy thông tin từ product listing
- **Scraping chi tiết**: Truy cập từng trang sản phẩm để lấy đầy đủ thông tin
- Hỗ trợ 30+ CSS selectors cho các theme khác nhau
- Auto-pagination với multiple page formats
- Retry mechanism với exponential backoff

### 🛡️ **Bảo mật và ổn định**
- Proxy rotation tích hợp
- Rate limiting và delay configurable
- Error handling toàn diện
- User-agent rotation
- Respectful scraping practices

### 📊 **Xuất dữ liệu và báo cáo**
- JSON và CSV export
- Real-time statistics
- Detailed logging
- Progress tracking
- Data validation

## 🔧 Cài đặt

### Yêu cầu hệ thống
- Python 3.7 hoặc cao hơn
- Kết nối Internet ổn định
- 50MB dung lượng trống

### Cài đặt dependencies

```bash
# Clone hoặc download project
git clone https://github.com/thredeisacoder/WooCommerce-Scraper
cd WooCommerce-Scraper

# Cài đặt packages
pip install -r requirements.txt
```

### Dependencies chính
```
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

## 🖥️ Cách sử dụng

### 🎯 **Phương pháp 1: GUI (Khuyến nghị cho người mới)**

```bash
python gui.py
```

**Tính năng GUI:**
- 🌐 **URL Input**: Nhập trực tiếp với validation
- ⚙️ **Settings**: Cài đặt pages, delay, proxy trực quan
- 📋 **Detailed Mode**: Toggle scraping chi tiết
- 💾 **Export Options**: Chọn format và output directory
- 📊 **Real-time Log**: Theo dõi progress với emoji và colors
- 🎯 **Quick URLs**: Templates sẵn có để test

**Quy trình sử dụng GUI:**
1. Mở GUI: `python gui.py`
2. Nhập URL WooCommerce
3. Chọn settings (pages, delay, detailed mode)
4. Chọn export format và folder
5. Click "🚀 Bắt đầu Scraping"
6. Theo dõi real-time log và đợi kết quả

### 💻 **Phương pháp 2: Command Line**

```bash
# Scraping cơ bản
python scraper.py https://shop.example.com

# Scraping chi tiết (chậm hơn nhưng đầy đủ)
python scraper.py https://shop.example.com --detailed

# Full options
python scraper.py https://shop.example.com \
  --max-pages 10 \
  --delay 2.0 \
  --detailed \
  --export-json products.json \
  --export-csv products.csv

# Chỉ xem statistics
python scraper.py https://shop.example.com --stats-only

# Không dùng proxy
python scraper.py https://shop.example.com --no-proxy
```

**Command Line Options:**
- `url`: URL WooCommerce shop (required)
- `--max-pages INT`: Số trang tối đa (default: 5)
- `--delay FLOAT`: Delay giữa requests (default: 1.0s)
- `--detailed`: Enable detailed scraping
- `--no-proxy`: Disable proxy
- `--export-json FILE`: Export to JSON
- `--export-csv FILE`: Export to CSV  
- `--quiet`: Suppress console output
- `--stats-only`: Chỉ hiển thị thống kê

### 🐍 **Phương pháp 3: Python API**

#### Basic Usage
```python
from scraper import WooCommerceScraper

# Khởi tạo scraper
scraper = WooCommerceScraper("https://shop.example.com")

# Scrape một trang
products = scraper.scrape_page("https://shop.example.com/shop")

# Scrape nhiều trang với chi tiết
products = scraper.scrape_all_pages(
    "https://shop.example.com/shop", 
    max_pages=5, 
    fetch_detailed=True
)

# Export results
scraper.export_to_json("products.json")
scraper.export_to_csv("products.csv")

# Get statistics
stats = scraper.get_statistics()
print(f"Total products: {stats['total_products']}")
```

#### Advanced Usage
```python
# Custom configuration
scraper = WooCommerceScraper(
    base_url="https://shop.example.com",
    use_proxy=True,
    delay=2.0
)

# Process results
for product in products:
    print(f"Product: {product.title}")
    print(f"Price: {product.price}")
    if product.description:
        print(f"Description: {product.description[:100]}...")
    if product.sku:
        print(f"SKU: {product.sku}")
    print("-" * 50)
```

#### Simple Function (Backward Compatible)
```python
from scraper import simple_scrape

# Quick scraping
products = simple_scrape("https://shop.example.com", detailed=True)
```

## ⚙️ Cấu hình

### config.json
Tạo file `config.json` để custom settings:

```json
{
  "default_settings": {
    "delay": 1.0,
    "max_pages": 5,
    "timeout": 30,
    "max_retries": 3,
    "use_proxy": true
  },
  "headers": {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
  },
  "selectors": {
    "product_containers": [
      "li.product",
      ".wc-block-grid__product",
      ".product-item",
      ".type-product"
    ],
    "title": [
      "h2.woocommerce-loop-product__title",
      ".wc-block-grid__product-title",
      ".product-title"
    ],
    "price": [
      "span.woocommerce-Price-amount",
      ".wc-block-grid__product-price",
      ".price"
    ],
    "description": [
      ".woocommerce-product-details__short-description",
      ".product-short-description",
      ".entry-summary p"
    ],
    "sku": [
      ".sku",
      ".product-meta .sku",
      "[itemprop='sku']"
    ],
    "stock": [
      ".stock",
      ".availability",
      ".woocommerce-stock-status"
    ],
    "category": [
      ".woocommerce-breadcrumb a",
      ".product_meta .posted_in a"
    ]
  },
  "export_options": {
    "default_json_file": "products.json",
    "default_csv_file": "products.csv"
  }
}
```

### Proxy Configuration
Proxy được cấu hình sẵn với IP2World. Để thay đổi:

```python
scraper = WooCommerceScraper(
    base_url="https://shop.example.com",
    use_proxy=False  # Tắt proxy
)
```

## 📦 Dữ liệu thu thập

### Product Schema
```python
@dataclass
class Product:
    title: str           # Tên sản phẩm
    price: str           # Giá (với currency)
    link: str            # URL đến trang sản phẩm
    image_url: str       # URL hình ảnh chính
    description: str     # Mô tả ngắn (optional)
    sku: str            # Mã sản phẩm (optional)
    stock_status: str   # Tình trạng kho (optional)
    category: str       # Danh mục (optional)
```

### Data Coverage
- **Cơ bản**: title, price, link, image (100% coverage)
- **Chi tiết**: description, SKU, stock, category (60-90% coverage)

### Export Formats

#### JSON Output
```json
[
  {
    "title": "Premium T-Shirt",
    "price": "$29.99",
    "link": "https://shop.example.com/product/premium-tshirt/",
    "image_url": "https://shop.example.com/wp-content/uploads/tshirt.jpg",
    "description": "Comfortable premium cotton t-shirt with modern fit...",
    "sku": "TSH-001",
    "stock_status": "In Stock",
    "category": "Clothing"
  }
]
```

#### CSV Output
```csv
title,price,link,image_url,description,sku,stock_status,category
Premium T-Shirt,$29.99,https://shop.example.com/product/premium-tshirt/,https://shop.example.com/wp-content/uploads/tshirt.jpg,Comfortable premium cotton...,TSH-001,In Stock,Clothing
```

## 📊 Ví dụ

### Console Output
```
[10:30:15] 🚀 BẮT ĐẦU SCRAPING MỚI
[10:30:15] 🌐 URL: https://roostick.com/shop
[10:30:15] 📄 Số trang tối đa: 5
[10:30:15] ⏱️ Delay: 1.0s
[10:30:15] 🔒 Proxy: Có
[10:30:15] 📋 Scrape chi tiết: Có
[10:30:16] 🔧 Khởi tạo scraper cho URL: https://roostick.com/shop
[10:30:17] 🔍 Bắt đầu scraping CHI TIẾT tối đa 5 trang (sẽ chậm hơn)...
[10:30:18] Found 12 products using selector: li.product
[10:30:18] Processing product 1/12 with detailed info...
[10:30:19] Product 'Premium Coffee Beans...' - Found: description, SKU, stock
[10:30:20] ✅ Tìm thấy 12 sản phẩm
[10:30:20] 💾 Đã xuất JSON: products_20241215_103020.json
[10:30:20] 📊 === THỐNG KÊ ===
[10:30:20]    Total Products: 12
[10:30:20]    Products With Price: 12
[10:30:20]    Products With Image: 12
[10:30:20]    Price Coverage: 100.0%
[10:30:20]    Image Coverage: 100.0%
```

### Statistics Example
```python
stats = scraper.get_statistics()
print(stats)
# Output:
{
    "total_products": 48,
    "products_with_price": 48,
    "products_with_image": 46,
    "price_coverage": "100.0%",
    "image_coverage": "95.8%"
}
```

## 📚 API Reference

### WooCommerceScraper Class

#### Constructor
```python
WooCommerceScraper(base_url, use_proxy=True, delay=1.0)
```

#### Methods
```python
# Scrape single page
scrape_page(url, fetch_detailed=False) -> List[Product]

# Scrape multiple pages  
scrape_all_pages(start_url, max_pages=10, fetch_detailed=False) -> List[Product]

# Export methods
export_to_json(filename=None)
export_to_csv(filename=None)

# Utility methods
get_statistics() -> Dict[str, Any]
print_products()
```

### Functions
```python
# Simple scraping function
simple_scrape(url, detailed=False) -> List[Product]
```

## 🛠️ Troubleshooting

### ❌ **Lỗi thường gặp**

#### "No products found"
```
Nguyên nhân: Website sử dụng cấu trúc HTML khác
Giải pháp:
1. Kiểm tra URL có đúng là trang shop không
2. Thử với --detailed để scrape từ product pages
3. Tăng delay: --delay 2.0
4. Check config.json selectors
```

#### "Connection timeout"
```
Nguyên nhân: Mạng chậm hoặc website chặn
Giải pháp:
1. Thử --no-proxy
2. Tăng delay: --delay 3.0
3. Kiểm tra internet connection
4. Thử URL khác để test
```

#### "Import error"
```
Nguyên nhân: Thiếu dependencies
Giải pháp:
pip install -r requirements.txt
```

### 🔧 **Performance Tips**

1. **Bắt đầu nhỏ**: Test với 1-2 trang trước
2. **Tối ưu delay**: 1-2s cho sites nhanh, 3-5s cho sites chậm
3. **Detailed mode**: Chỉ dùng khi cần thiết (chậm hơn 3-5x)
4. **Proxy**: Giữ nguyên enabled để tránh bị block

### 📋 **Debug Mode**

```bash
# Enable verbose logging
python scraper.py https://shop.example.com --detailed --max-pages 1

# Check logs
tail -f scraper.log
```

## 📄 File Structure

```
woocommerce-scraper/
├── scraper.py          # Core scraper engine
├── gui.py             # GUI interface  
├── config.json        # Configuration file
├── requirements.txt   # Dependencies
├── README.md         # This file
├── GUI_GUIDE.md      # GUI usage guide
├── scraper.log       # Runtime logs
└── products_*.json   # Output files
```

## ⚡ Performance

- **Basic scraping**: ~1-2 seconds per page
- **Detailed scraping**: ~5-10 seconds per page  
- **Memory usage**: ~50-100MB for 1000 products
- **Success rate**: 95%+ for standard WooCommerce themes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚖️ Disclaimer

**Sử dụng có trách nhiệm:**
- Tuân thủ robots.txt của website
- Không spam quá nhiều requests
- Respect website's terms of service
- Chỉ scrape dữ liệu công khai
- Sử dụng cho mục đích hợp pháp

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra [Troubleshooting](#-troubleshooting)
2. Xem [GUI Guide](GUI_GUIDE.md)
3. Check logs trong `scraper.log`
4. Tạo issue với log details

---

**Made with ❤️ for the WooCommerce community** 

#!/usr/bin/env python3
"""
WooCommerce Scraper GUI
Giao diện đồ họa cho chương trình scrape WooCommerce
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import os
import json
from datetime import datetime
import sys

# Import scraper từ file scraper.py
try:
    from scraper import WooCommerceScraper, Product
except ImportError:
    messagebox.showerror("Lỗi", "Không thể import scraper.py. Vui lòng đảm bảo file scraper.py tồn tại!")
    sys.exit(1)

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WooCommerce Product Scraper - GUI")
        self.root.geometry("900x750")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.url_var = tk.StringVar(value="https://roostick.com/shop")
        self.max_pages_var = tk.IntVar(value=5)
        self.delay_var = tk.DoubleVar(value=1.0)
        self.use_proxy_var = tk.BooleanVar(value=True)
        self.fetch_detailed_var = tk.BooleanVar(value=False)
        self.export_json_var = tk.BooleanVar(value=True)
        self.export_csv_var = tk.BooleanVar(value=False)
        self.output_dir_var = tk.StringVar(value=os.getcwd())
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        self.scraper = None
        self.scraping_thread = None
        self.is_scraping = False
        
        self.create_widgets()
        self.start_message_processor()
        
    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🛒 WooCommerce Product Scraper", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL Section
        url_frame = ttk.LabelFrame(main_frame, text="🌐 URL và Cài đặt cơ bản", padding="15")
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="URL WooCommerce:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60, font=('Arial', 10))
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Validate URL button
        validate_btn = ttk.Button(url_frame, text="✓ Kiểm tra", command=self.validate_url)
        validate_btn.grid(row=0, column=2)
        
        # Quick URLs
        quick_frame = ttk.Frame(url_frame)
        quick_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0), sticky=(tk.W, tk.E))
        
        ttk.Label(quick_frame, text="URL mẫu:", font=('Arial', 9)).pack(side=tk.LEFT)
        ttk.Button(quick_frame, text="Roostick", 
                  command=lambda: self.url_var.set("https://roostick.com/shop")).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(quick_frame, text="Demo Shop", 
                  command=lambda: self.url_var.set("https://demo.woothemes.com/storefront/shop/")).pack(side=tk.LEFT, padx=5)
        
        # Options Section
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Tùy chọn Scraping", padding="15")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        options_frame.columnconfigure(1, weight=1)
        
        # Row 1: Max pages and delay
        ttk.Label(options_frame, text="Số trang tối đa:").grid(row=0, column=0, sticky=tk.W)
        max_pages_spin = ttk.Spinbox(options_frame, from_=1, to=100, textvariable=self.max_pages_var, width=10)
        max_pages_spin.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        ttk.Label(options_frame, text="Delay (giây):").grid(row=0, column=2, sticky=tk.W)
        delay_spin = ttk.Spinbox(options_frame, from_=0.1, to=10.0, increment=0.1, 
                                textvariable=self.delay_var, width=10, format="%.1f")
        delay_spin.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # Row 2: Proxy and detailed options
        proxy_check = ttk.Checkbutton(options_frame, text="🔒 Sử dụng Proxy (khuyến nghị)", 
                                     variable=self.use_proxy_var)
        proxy_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(15, 0))
        
        detailed_check = ttk.Checkbutton(options_frame, text="📋 Scrape chi tiết (chậm hơn nhưng đầy đủ hơn)", 
                                        variable=self.fetch_detailed_var)
        detailed_check.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=(15, 0))
        
        # Export Section  
        export_frame = ttk.LabelFrame(main_frame, text="💾 Xuất dữ liệu", padding="15")
        export_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        export_frame.columnconfigure(1, weight=1)
        
        # Export format options
        format_frame = ttk.Frame(export_frame)
        format_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ttk.Label(format_frame, text="Định dạng:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        json_check = ttk.Checkbutton(format_frame, text="📄 JSON", variable=self.export_json_var)
        json_check.pack(side=tk.LEFT, padx=(20, 10))
        
        csv_check = ttk.Checkbutton(format_frame, text="📊 CSV", variable=self.export_csv_var)
        csv_check.pack(side=tk.LEFT)
        
        # Output directory
        ttk.Label(export_frame, text="Thư mục lưu:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(15, 0))
        output_entry = ttk.Entry(export_frame, textvariable=self.output_dir_var, width=50)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=(15, 0))
        
        browse_btn = ttk.Button(export_frame, text="📁 Duyệt...", command=self.browse_output_dir)
        browse_btn.grid(row=1, column=2, pady=(15, 0))
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=(15, 0))
        
        self.start_btn = ttk.Button(control_frame, text="🚀 Bắt đầu Scraping", 
                                   command=self.start_scraping, 
                                   style="Accent.TButton", width=20)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️ Dừng", 
                                  command=self.stop_scraping, state=tk.DISABLED, width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(control_frame, text="🧹 Xóa Log", command=self.clear_log, width=15)
        self.clear_btn.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=5, column=0, columnspan=3, pady=(15, 0), sticky=(tk.W, tk.E))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Sẵn sàng scraping...")
        progress_label = ttk.Label(progress_frame, textvariable=self.progress_var, font=('Arial', 10))
        progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log Scraping", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=90, 
                                                 font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Trạng thái:").grid(row=0, column=0, sticky=tk.W)
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               relief=tk.SUNKEN, padding="5")
        status_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
    def validate_url(self):
        """Kiểm tra URL có hợp lệ không"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL!")
            return
            
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Lỗi", "URL phải bắt đầu bằng http:// hoặc https://")
            return
            
        # Test connection
        self.log_message(f"Đang kiểm tra URL: {url}")
        try:
            import requests
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                self.log_message("✅ URL hợp lệ và có thể truy cập!")
                messagebox.showinfo("Thành công", "URL hợp lệ và có thể truy cập!")
            else:
                self.log_message(f"⚠️ URL trả về status code: {response.status_code}")
                messagebox.showwarning("Cảnh báo", f"URL trả về status code: {response.status_code}")
        except Exception as e:
            error_msg = f"❌ Không thể kết nối đến URL: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("Lỗi", f"Không thể kết nối đến URL: {str(e)}")
    
    def browse_output_dir(self):
        """Chọn thư mục lưu file"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
            self.log_message(f"📁 Chọn thư mục: {directory}")
    
    def log_message(self, message):
        """Thêm message vào log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🧹 Log đã được xóa")
    
    def start_scraping(self):
        """Bắt đầu scraping"""
        if self.is_scraping:
            return
            
        # Validate inputs
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL!")
            return
            
        if not (self.export_json_var.get() or self.export_csv_var.get()):
            messagebox.showerror("Lỗi", "Vui lòng chọn ít nhất một định dạng xuất!")
            return
        
        # Update UI
        self.is_scraping = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar.start(10)
        self.progress_var.set("🔄 Đang scraping...")
        self.status_var.set("Đang scraping...")
        
        # Log start
        self.log_message("=" * 50)
        self.log_message("🚀 BẮT ĐẦU SCRAPING MỚI")
        self.log_message("=" * 50)
        self.log_message(f"🌐 URL: {url}")
        self.log_message(f"📄 Số trang tối đa: {self.max_pages_var.get()}")
        self.log_message(f"⏱️ Delay: {self.delay_var.get()}s")
        self.log_message(f"🔒 Proxy: {'Có' if self.use_proxy_var.get() else 'Không'}")
        self.log_message(f"📋 Scrape chi tiết: {'Có' if self.fetch_detailed_var.get() else 'Không'}")
        
        # Start scraping thread
        self.scraping_thread = threading.Thread(target=self.scraping_worker, daemon=True)
        self.scraping_thread.start()
    
    def stop_scraping(self):
        """Dừng scraping"""
        if self.scraping_thread and self.scraping_thread.is_alive():
            self.log_message("⏹️ Đang cố gắng dừng scraping...")
            messagebox.showinfo("Thông báo", "Scraping sẽ dừng sau request hiện tại")
        self.reset_ui()
    
    def reset_ui(self):
        """Reset UI về trạng thái ban đầu"""
        self.is_scraping = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_var.set("✅ Hoàn thành")
        self.status_var.set("Sẵn sàng")
    
    def scraping_worker(self):
        """Worker thread cho scraping"""
        try:
            # Get parameters
            url = self.url_var.get().strip()
            max_pages = self.max_pages_var.get()
            delay = self.delay_var.get()
            use_proxy = self.use_proxy_var.get()
            fetch_detailed = self.fetch_detailed_var.get()
            
            # Create scraper
            self.message_queue.put(("log", f"🔧 Khởi tạo scraper cho URL: {url}"))
            scraper = WooCommerceScraper(
                base_url=url,
                use_proxy=use_proxy,
                delay=delay
            )
            
            # Start scraping
            if fetch_detailed:
                self.message_queue.put(("log", f"🔍 Bắt đầu scraping CHI TIẾT tối đa {max_pages} trang (sẽ chậm hơn)..."))
            else:
                self.message_queue.put(("log", f"🔍 Bắt đầu scraping tối đa {max_pages} trang..."))
            
            products = scraper.scrape_all_pages(url, max_pages=max_pages, fetch_detailed=fetch_detailed)
            
            if not products:
                self.message_queue.put(("log", "❌ Không tìm thấy sản phẩm nào!"))
                self.message_queue.put(("error", "Không tìm thấy sản phẩm nào! Có thể website sử dụng cấu trúc HTML khác hoặc có biện pháp chống scraping."))
                return
            
            self.message_queue.put(("log", f"✅ Tìm thấy {len(products)} sản phẩm"))
            
            # Export data
            output_dir = self.output_dir_var.get()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            exported_files = []
            
            if self.export_json_var.get():
                json_file = os.path.join(output_dir, f"products_{timestamp}.json")
                scraper.export_to_json(json_file)
                exported_files.append(json_file)
                self.message_queue.put(("log", f"💾 Đã xuất JSON: {json_file}"))
            
            if self.export_csv_var.get():
                csv_file = os.path.join(output_dir, f"products_{timestamp}.csv")
                scraper.export_to_csv(csv_file)
                exported_files.append(csv_file)
                self.message_queue.put(("log", f"💾 Đã xuất CSV: {csv_file}"))
            
            # Get statistics
            stats = scraper.get_statistics()
            if stats:
                self.message_queue.put(("log", "📊 === THỐNG KÊ ==="))
                for key, value in stats.items():
                    self.message_queue.put(("log", f"   {key.replace('_', ' ').title()}: {value}"))
            
            # Show sample products
            self.message_queue.put(("log", "🔍 === MẪU SẢN PHẨM ==="))
            for i, product in enumerate(products[:3], 1):  # Show first 3 products
                self.message_queue.put(("log", f"   {i}. {product.title} - {product.price}"))
            
            if len(products) > 3:
                self.message_queue.put(("log", f"   ... và {len(products) - 3} sản phẩm khác"))
            
            success_msg = f"🎉 Scraping hoàn thành thành công!\n\n📊 Tìm thấy: {len(products)} sản phẩm\n💾 Đã lưu: {len(exported_files)} file\n📁 Thư mục: {output_dir}"
            self.message_queue.put(("success", success_msg))
            
        except Exception as e:
            error_msg = f"❌ Lỗi trong quá trình scraping: {str(e)}"
            self.message_queue.put(("log", error_msg))
            self.message_queue.put(("error", f"Đã xảy ra lỗi:\n{str(e)}\n\nVui lòng kiểm tra lại URL và thử lại."))
        finally:
            self.message_queue.put(("done", ""))
    
    def start_message_processor(self):
        """Xử lý messages từ queue"""
        try:
            while True:
                message_type, message = self.message_queue.get_nowait()
                
                if message_type == "log":
                    self.log_message(message)
                elif message_type == "error":
                    self.reset_ui()
                    messagebox.showerror("Lỗi", message)
                elif message_type == "success":
                    self.reset_ui()
                    messagebox.showinfo("Thành công", message)
                elif message_type == "done":
                    self.reset_ui()
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.start_message_processor)

def main():
    """Main function"""
    root = tk.Tk()
    
    # Set window properties
    root.minsize(800, 600)
    
    try:
        # Set window icon (you can add an icon file)
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = ScraperGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    # Add welcome message
    app.log_message("🎉 Chào mừng đến với WooCommerce Product Scraper!")
    app.log_message("💡 Nhập URL WooCommerce và bấm 'Bắt đầu Scraping' để bắt đầu.")
    app.log_message("📋 Bạn có thể theo dõi tiến trình scraping tại đây.")
    
    root.mainloop()

if __name__ == "__main__":
    main()

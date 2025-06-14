#!/usr/bin/env python3
"""
Enhanced WooCommerce Product Scraper
Improved version with better error handling, configuration, and export options
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import random
import time
import logging
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Product:
    """Product data structure"""
    title: str
    price: str
    link: str
    image_url: str
    description: Optional[str] = None
    sku: Optional[str] = None
    stock_status: Optional[str] = None
    category: Optional[str] = None

class WooCommerceScraper:
    """Enhanced WooCommerce product scraper"""
    
    def __init__(self, base_url: str, use_proxy: bool = True, delay: float = 1.0):
        self.base_url = base_url.rstrip('/')
        self.use_proxy = use_proxy
        self.delay = delay
        self.session = requests.Session()
        self.products: List[Product] = []
        
        # Load configuration if exists
        self.config = self._load_config()
        
        # Setup headers
        headers = self.config.get('headers', {})
        if not headers:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        self.session.headers.update(headers)
        
        # Setup proxy if enabled
        if self.use_proxy:
            self._setup_proxy()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json if exists"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid config.json: {e}")
            return {}
            
    def _setup_proxy(self):
        """Setup proxy configuration"""
        session_id = random.randint(1000000000, 9999999999)
        proxy_config = {
            "http": f"", # Add proxy here
            "https": f""
        }
        self.session.proxies = proxy_config
        logger.info(f"Proxy configured with session ID: {session_id}")
        
    def _get_page_content(self, url: str, timeout: int = 30, max_retries: int = 3) -> Optional[str]:
        """Get page content with error handling and retries"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                
                # Add delay between requests
                time.sleep(self.delay)
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All attempts failed for {url}")
        return None
            
    def _extract_product_details(self, product_element, fetch_detailed=False) -> Optional[Product]:
        """Extract product details from HTML element"""
        try:
            # Get selectors from config
            selectors = self.config.get('selectors', {})
            
            # Extract title - try multiple selectors
            title_selectors = selectors.get('title', [
                'h2.woocommerce-loop-product__title',
                'h3.woocommerce-loop-product__title',
                '.product-title',
                '.wc-block-grid__product-title',
                '.product-item-title',
                'a'
            ])
            
            title_elem = None
            for selector in title_selectors:
                title_elem = product_element.select_one(selector)
                if title_elem:
                    break
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            # Extract price - try multiple selectors
            price_selectors = selectors.get('price', [
                'span.woocommerce-Price-amount',
                '.woocommerce-Price-amount bdi',
                '.price .amount',
                '.price bdi',
                '.price',
                '.wc-block-grid__product-price',
                '.product-price'
            ])
            
            price_elem = None
            for selector in price_selectors:
                price_elem = product_element.select_one(selector)
                if price_elem:
                    break
            price = price_elem.get_text(strip=True) if price_elem else "N/A"
            
            # Extract link
            link_selectors = selectors.get('link', [
                'a.woocommerce-LoopProduct-link',
                'a.wc-block-grid__product-link',
                '.product-item-link',
                'h2 a',
                'h3 a',
                'a'
            ])
            
            link_elem = None
            for selector in link_selectors:
                link_elem = product_element.select_one(selector)
                if link_elem and link_elem.get('href'):
                    break
            link = urljoin(self.base_url, link_elem['href']) if link_elem and link_elem.get('href') else "N/A"
            
            # Extract image
            image_selectors = selectors.get('image', [
                'img.attachment-woocommerce_thumbnail',
                'img.wp-post-image',
                '.wc-block-grid__product-image img',
                '.product-image img',
                'img'
            ])
            
            img_elem = None
            for selector in image_selectors:
                img_elem = product_element.select_one(selector)
                if img_elem:
                    break
            
            image_url = "N/A"
            if img_elem:
                image_url = img_elem.get('src', img_elem.get('data-src', img_elem.get('data-lazy-src', '')))
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(self.base_url, image_url)
                
            # Extract additional details from current element
            description = self._extract_description(product_element)
            sku = self._extract_sku(product_element)
            stock_status = self._extract_stock_status(product_element)
            category = self._extract_category(product_element)
            
            # If we have a valid link and want detailed info, fetch from product page
            if fetch_detailed and link != "N/A" and not description:
                detailed_info = self._fetch_product_details(link)
                if detailed_info:
                    description = detailed_info.get('description', description)
                    sku = detailed_info.get('sku', sku)
                    stock_status = detailed_info.get('stock_status', stock_status)
                    category = detailed_info.get('category', category)
            
            return Product(
                title=title,
                price=price,
                link=link,
                image_url=image_url,
                description=description,
                sku=sku,
                stock_status=stock_status,
                category=category
            )
            
        except Exception as e:
            logger.error(f"Error extracting product details: {e}")
            return None
    
    def _fetch_product_details(self, product_url: str) -> Optional[Dict[str, str]]:
        """Fetch detailed product information from individual product page"""
        try:
            logger.info(f"Fetching detailed info from: {product_url}")
            page_content = self._get_page_content(product_url)
            if not page_content:
                return None
                
            soup = BeautifulSoup(page_content, 'html.parser')
            
            details = {}
            
            # Extract description from product page
            desc_selectors = [
                '.woocommerce-product-details__short-description',
                '.product-short-description',
                '.entry-summary .woocommerce-product-details__short-description',
                '.summary .woocommerce-product-details__short-description',
                '.entry-content p',
                '.product-description',
                '.short-description',
                '.wc-tab-content p'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    text = desc_elem.get_text(strip=True)
                    if text and len(text) > 10:
                        details['description'] = text[:500]
                        break
            
            # Extract SKU from product page
            sku_selectors = [
                '.sku',
                '.product_meta .sku',
                '.woocommerce-product-sku',
                '.product-sku',
                '[itemprop="sku"]'
            ]
            
            for selector in sku_selectors:
                sku_elem = soup.select_one(selector)
                if sku_elem:
                    sku_text = sku_elem.get_text(strip=True)
                    if sku_text and sku_text.lower() not in ['sku', 'sku:', 'n/a', '']:
                        details['sku'] = sku_text
                        break
            
            # Extract stock status from product page
            stock_selectors = [
                '.stock',
                '.availability p',
                '.woocommerce-stock-status',
                '.in-stock',
                '.out-of-stock',
                '.stock-status'
            ]
            
            for selector in stock_selectors:
                stock_elem = soup.select_one(selector)
                if stock_elem:
                    stock_text = stock_elem.get_text(strip=True).lower()
                    if stock_text:
                        if any(word in stock_text for word in ['in stock', 'available', 'có sẵn']):
                            details['stock_status'] = 'In Stock'
                        elif any(word in stock_text for word in ['out of stock', 'sold out', 'hết hàng']):
                            details['stock_status'] = 'Out of Stock'
                        elif any(word in stock_text for word in ['backorder', 'pre-order']):
                            details['stock_status'] = 'On Backorder'
                        break
            
            # Extract category from breadcrumb or product meta
            cat_selectors = [
                '.woocommerce-breadcrumb a',
                '.breadcrumb a',
                '.product_meta .posted_in a',
                '.product-category a',
                '.entry-meta .category a'
            ]
            
            for selector in cat_selectors:
                cat_elems = soup.select(selector)
                if cat_elems:
                    # Get the last breadcrumb item (usually the direct category)
                    cat_text = cat_elems[-1].get_text(strip=True)
                    if cat_text and cat_text.lower() not in ['home', 'shop', 'trang chủ']:
                        details['category'] = cat_text
                        break
            
            return details if details else None
            
        except Exception as e:
            logger.error(f"Error fetching product details from {product_url}: {e}")
            return None
            
    def _extract_description(self, element) -> Optional[str]:
        """Extract product description"""
        # Try multiple selectors for description
        desc_selectors = [
            '.woocommerce-product-details__short-description',
            '.product-short-description',
            '.entry-summary p',
            '.product-excerpt',
            '.product-description',
            '.wc-product-description',
            'p.product-excerpt',
            '.summary .description',
            '.product-summary p',
            '[class*="description"]',
            'p'
        ]
        
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                text = desc_elem.get_text(strip=True)
                if text and len(text) > 10:  # Only return meaningful descriptions
                    return text[:500]  # Limit length
        return None
        
    def _extract_sku(self, element) -> Optional[str]:
        """Extract product SKU"""
        # Try multiple selectors for SKU
        sku_selectors = [
            '.sku',
            '.product-sku',
            '.woocommerce-product-sku',
            '[class*="sku"]',
            '.product-meta .sku',
            '.product-code',
            '[data-sku]'
        ]
        
        for selector in sku_selectors:
            sku_elem = element.select_one(selector)
            if sku_elem:
                # Try text content first
                sku_text = sku_elem.get_text(strip=True)
                if sku_text and not sku_text.lower() in ['sku', 'sku:', 'n/a', '']:
                    return sku_text
                # Try data attribute
                sku_data = sku_elem.get('data-sku')
                if sku_data:
                    return sku_data
        return None
        
    def _extract_stock_status(self, element) -> Optional[str]:
        """Extract stock status"""
        # Try multiple selectors for stock status
        stock_selectors = [
            '.stock',
            '.availability',
            '.in-stock',
            '.out-of-stock',
            '.stock-status',
            '.woocommerce-stock-status',
            '[class*="stock"]',
            '.product-stock',
            '.inventory-status'
        ]
        
        for selector in stock_selectors:
            stock_elem = element.select_one(selector)
            if stock_elem:
                stock_text = stock_elem.get_text(strip=True).lower()
                if stock_text:
                    # Normalize stock status
                    if any(word in stock_text for word in ['in stock', 'available', 'có sẵn']):
                        return 'In Stock'
                    elif any(word in stock_text for word in ['out of stock', 'sold out', 'hết hàng']):
                        return 'Out of Stock'
                    elif any(word in stock_text for word in ['backorder', 'pre-order', 'đặt trước']):
                        return 'On Backorder'
                    else:
                        return stock_text.title()
        
        # Check for stock indicators in class names
        if element.select_one('.in-stock'):
            return 'In Stock'
        elif element.select_one('.out-of-stock'):
            return 'Out of Stock'
        
        return None
        
    def _extract_category(self, element) -> Optional[str]:
        """Extract product category"""
        # Try multiple selectors for category
        cat_selectors = [
            '.product-category',
            '.category',
            '.woocommerce-product-category',
            '.product-cat',
            '[class*="category"]',
            '.breadcrumb a',
            '.product-meta .category'
        ]
        
        for selector in cat_selectors:
            cat_elem = element.select_one(selector)
            if cat_elem:
                cat_text = cat_elem.get_text(strip=True)
                if cat_text and cat_text.lower() not in ['category', 'categories', 'cat', '']:
                    return cat_text
        return None
        
    def scrape_page(self, url: str, fetch_detailed: bool = False) -> List[Product]:
        """Scrape products from a single page"""
        page_content = self._get_page_content(url)
        if not page_content:
            return []
            
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Find product containers using multiple selectors
        selectors = self.config.get('selectors', {})
        product_selectors = selectors.get('product_containers', [
            'li.product',
            '.wc-block-grid__product',
            '.product-item',
            '.woocommerce-product',
            '.type-product',
            '[class*="product"]',
            '.product',
            '.products li'
        ])
        
        elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                logger.info(f"Found {len(elements)} products using selector: {selector}")
                break
        else:
            logger.warning("No products found with any selector")
            return []
            
        products = []
        for i, element in enumerate(elements):
            try:
                # Show progress for detailed scraping
                if fetch_detailed:
                    logger.info(f"Processing product {i+1}/{len(elements)} with detailed info...")
                
                product = self._extract_product_details(element, fetch_detailed=fetch_detailed)
                if product and product.title != "N/A":
                    products.append(product)
                    
                    # Log what we found
                    details_found = []
                    if product.description:
                        details_found.append("description")
                    if product.sku:
                        details_found.append("SKU")
                    if product.stock_status:
                        details_found.append("stock")
                    if product.category:
                        details_found.append("category")
                    
                    if details_found:
                        logger.info(f"Product '{product.title[:30]}...' - Found: {', '.join(details_found)}")
                    
            except Exception as e:
                logger.error(f"Error processing product {i+1}: {e}")
                continue
                
        logger.info(f"Successfully extracted {len(products)} products from {url}")
        return products
        
    def scrape_all_pages(self, start_url: str, max_pages: int = 10, fetch_detailed: bool = False) -> List[Product]:
        """Scrape products from multiple pages"""
        all_products = []
        current_url = start_url
        page_num = 1
        
        while current_url and page_num <= max_pages:
            logger.info(f"Scraping page {page_num}/{max_pages}: {current_url}")
            
            page_products = self.scrape_page(current_url, fetch_detailed=fetch_detailed)
            if not page_products:
                logger.info("No products found, stopping pagination")
                break
                
            all_products.extend(page_products)
            logger.info(f"Page {page_num} completed. Total products so far: {len(all_products)}")
            
            # Find next page URL
            page_content = self._get_page_content(current_url)
            if page_content:
                soup = BeautifulSoup(page_content, 'html.parser')
                # Try multiple selectors for next page link
                next_selectors = [
                    'a.next',
                    '.next-page a',
                    '.pagination .next',
                    '.woocommerce-pagination .next',
                    'a[aria-label="Next"]',
                    '.page-numbers.next'
                ]
                
                next_link = None
                for selector in next_selectors:
                    next_link = soup.select_one(selector)
                    if next_link and next_link.get('href'):
                        break
                
                if next_link and next_link.get('href'):
                    current_url = urljoin(self.base_url, next_link['href'])
                    page_num += 1
                else:
                    logger.info("No more pages found")
                    break
            else:
                break
                
        self.products = all_products
        
        # Final summary
        logger.info(f"=== SCRAPING COMPLETED ===")
        logger.info(f"Total products scraped: {len(all_products)}")
        
        if fetch_detailed:
            products_with_desc = sum(1 for p in all_products if p.description)
            products_with_sku = sum(1 for p in all_products if p.sku)
            products_with_stock = sum(1 for p in all_products if p.stock_status)
            products_with_cat = sum(1 for p in all_products if p.category)
            
            logger.info(f"Products with description: {products_with_desc}")
            logger.info(f"Products with SKU: {products_with_sku}")
            logger.info(f"Products with stock status: {products_with_stock}")
            logger.info(f"Products with category: {products_with_cat}")
        
        return all_products
        
    def export_to_json(self, filename: str = None):
        """Export products to JSON file"""
        if not filename:
            filename = self.config.get('export_options', {}).get('default_json_file', 'products.json')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([asdict(product) for product in self.products], f, 
                         ensure_ascii=False, indent=2)
            logger.info(f"Products exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            
    def export_to_csv(self, filename: str = None):
        """Export products to CSV file"""
        if not filename:
            filename = self.config.get('export_options', {}).get('default_csv_file', 'products.csv')
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if self.products:
                    fieldnames = asdict(self.products[0]).keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for product in self.products:
                        writer.writerow(asdict(product))
            logger.info(f"Products exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        if not self.products:
            return {}
        
        total_products = len(self.products)
        products_with_price = sum(1 for p in self.products if p.price != "N/A")
        products_with_image = sum(1 for p in self.products if p.image_url != "N/A")
        
        return {
            "total_products": total_products,
            "products_with_price": products_with_price,
            "products_with_image": products_with_image,
            "price_coverage": f"{products_with_price/total_products*100:.1f}%",
            "image_coverage": f"{products_with_image/total_products*100:.1f}%"
        }
            
    def print_products(self):
        """Print products to console"""
        for i, product in enumerate(self.products, 1):
            print(f"\n--- Product {i} ---")
            print(f"Title: {product.title}")
            print(f"Price: {product.price}")
            print(f"Link: {product.link}")
            print(f"Image URL: {product.image_url}")
            if product.description:
                print(f"Description: {product.description[:100]}...")
            if product.sku:
                print(f"SKU: {product.sku}")
            if product.stock_status:
                print(f"Stock Status: {product.stock_status}")
            if product.category:
                print(f"Category: {product.category}")
            print("=" * 60)
        
        # Print statistics
        stats = self.get_statistics()
        if stats:
            print(f"\n--- Statistics ---")
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Enhanced WooCommerce Product Scraper')
    parser.add_argument('url', nargs='?', default='https://roostick.com/shop', 
                       help='WooCommerce shop URL to scrape (default: https://roostick.com/shop)')
    parser.add_argument('--max-pages', type=int, default=5, 
                       help='Maximum pages to scrape (default: 5)')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--no-proxy', action='store_true', 
                       help='Disable proxy usage')
    parser.add_argument('--export-json', 
                       help='Export to JSON file (default: products.json)')
    parser.add_argument('--export-csv', 
                       help='Export to CSV file (default: products.csv)')
    parser.add_argument('--quiet', action='store_true', 
                       help='Suppress console output')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only show statistics, don\'t print products')
    parser.add_argument('--detailed', action='store_true',
                       help='Fetch detailed product info (slower but more complete)')
    
    args = parser.parse_args()
    
    # Validate URL
    parsed_url = urlparse(args.url)
    if not parsed_url.scheme or not parsed_url.netloc:
        logger.error("Invalid URL provided")
        sys.exit(1)
        
    # Initialize scraper
    scraper = WooCommerceScraper(
        base_url=args.url,
        use_proxy=not args.no_proxy,
        delay=args.delay
    )
    
    try:
        # Scrape products
        logger.info(f"Starting scrape of {args.url}")
        if args.detailed:
            logger.info("Detailed scraping enabled - this will be slower but more comprehensive")
        products = scraper.scrape_all_pages(args.url, max_pages=args.max_pages, fetch_detailed=args.detailed)
        
        if not products:
            logger.warning("No products found")
            return
            
        # Export data
        if args.export_json or (not args.export_csv and not args.quiet):
            scraper.export_to_json(args.export_json)
            
        if args.export_csv:
            scraper.export_to_csv(args.export_csv)
            
        # Print to console if not quiet
        if not args.quiet:
            if args.stats_only:
                stats = scraper.get_statistics()
                print("\n--- Scraping Statistics ---")
                for key, value in stats.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
            else:
                scraper.print_products()
            
        logger.info(f"Scraping completed successfully. Found {len(products)} products.")
        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

# Simple usage example for backward compatibility
def simple_scrape(url: str = "https://roostick.com/shop", detailed: bool = False):
    """Simple function to scrape products (backward compatibility)"""
    scraper = WooCommerceScraper(url)
    products = scraper.scrape_page(url, fetch_detailed=detailed)
    
    for product in products:
        print(f"Title: {product.title}")
        print(f"Price: {product.price}")
        print(f"Link: {product.link}")
        print(f"Image URL: {product.image_url}")
        if product.description:
            print(f"Description: {product.description[:100]}...")
        if product.sku:
            print(f"SKU: {product.sku}")
        if product.stock_status:
            print(f"Stock Status: {product.stock_status}")
        if product.category:
            print(f"Category: {product.category}")
        print("="*50)
    
    return products

if __name__ == "__main__":
    main()

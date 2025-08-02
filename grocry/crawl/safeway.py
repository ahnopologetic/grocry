import json
import time
from urllib.parse import urljoin

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    JsonCssExtractionStrategy,
)
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.filters import (
    ContentTypeFilter,
    DomainFilter,
    FilterChain,
    URLPatternFilter,
)
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer


class SafewayScraper:
    def __init__(self, max_products: int = 100, max_concurrent: int = 5):
        self.max_products = max_products
        self.max_concurrent = max_concurrent
        self.scraped_products = []

        # Browser configuration
        self.browser_config = BrowserConfig(
            headless=True, java_script_enabled=True, verbose=False
        )

    def get_product_extraction_config(self):
        """Get configuration for product page extraction."""
        # Define comprehensive schema for Safeway product extraction
        schema = {
            "name": "Safeway Product",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "product_name",
                    "selector": "h1, .product-title, [data-testid='product-title'], .product-name, .product-header h1, .product-details h1, .product-info h1, .product-name, .product-title, .product-header, .product-detail-title, .product-detail-name, .product-name, .item-name, .product-detail-name, .product-header-title",
                    "type": "text",
                },
                {
                    "name": "product_price",
                    "selector": ".price, .product-price, [data-testid='price'], .price-value, span[class*='price'], .product-price span, .price-display, .product-cost, .price-current, .price-sale, .price-regular, .product-price-current, .price-value, .price-amount",
                    "type": "text",
                },
                {
                    "name": "product_description",
                    "selector": ".product-description, .description, [data-testid='description'], .product-details, .product-info, .product-summary, .product-overview",
                    "type": "text",
                },
                {
                    "name": "ingredients",
                    "selector": ".ingredients, .ingredient-list, [data-testid='ingredients'], .product-ingredients, .ingredients-list, .ingredient-info",
                    "type": "text",
                },
                {
                    "name": "nutritional_info",
                    "selector": ".nutrition, .nutritional-info, [data-testid='nutrition'], .product-nutrition, .nutrition-facts, .nutrition-label",
                    "type": "text",
                },
                {
                    "name": "product_image",
                    "selector": ".product-image img, .product-photo img, [data-testid='product-image'] img, .product-gallery img, img[alt*='product'], .product-hero img, .main-image img",
                    "type": "attribute",
                    "attribute": "src",
                },
                {
                    "name": "product_id",
                    "selector": ".product-id, .sku, [data-testid='sku'], .product-sku, .item-number, .product-detail-sku, .sku-number, .product-code",
                    "type": "text",
                },
                {
                    "name": "brand",
                    "selector": ".brand, .product-brand, [data-testid='brand'], .brand-name, .product-detail-brand, .brand-info",
                    "type": "text",
                },
                {
                    "name": "size",
                    "selector": ".size, .product-size, [data-testid='size'], .size-info, .product-detail-size, .size-value, .product-weight",
                    "type": "text",
                },
            ],
        }

        extraction_strategy = JsonCssExtractionStrategy(schema, verbose=False)

        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_for="css:body",
            wait_until="domcontentloaded",
            page_timeout=30000,
            delay_before_return_html=2,
            extraction_strategy=extraction_strategy,
            js_code=[
                """
                (async () => {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    // Scroll to load lazy-loaded content
                    window.scrollTo(0, document.body.scrollHeight);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    window.scrollTo(0, 0);
                })();
                """
            ],
        )

    def get_deep_crawl_config(self):
        """Get configuration for deep crawling with Best-First strategy."""
        # Create filter chain to focus on product pages
        filter_chain = FilterChain(
            [
                # Only crawl Safeway domain
                DomainFilter(allowed_domains=["safeway.com"]),
                # Focus on product pages and category pages
                URLPatternFilter(
                    patterns=[
                        "*shop/aisles/*",  # Category pages
                        "*shop/product/*",  # Product detail pages
                        "*product/*",  # Alternative product pages
                        "*pdp/*",  # Product detail pages
                        "*item/*",  # Item pages
                        "*detail/*",  # Detail pages
                        "*shop*",  # Any shop-related pages
                    ]
                ),
                # Only HTML content
                ContentTypeFilter(allowed_types=["text/html"]),
            ]
        )

        # Create scorer to prioritize product pages
        product_scorer = KeywordRelevanceScorer(
            keywords=[
                "product",
                "price",
                "ingredients",
                "nutrition",
                "organic",
                "food",
                "aisles",
                "shop",
                "item",
                "detail",
                "pdp",
                "grocery",
                "frozen",
                "fresh",
                "organic",
                "natural",
            ],
            weight=0.9,
        )

        # Use Best-First strategy for intelligent prioritization
        deep_crawl_strategy = BestFirstCrawlingStrategy(
            max_depth=3,  # Reasonable depth for product discovery
            include_external=False,  # Stay within Safeway domain
            max_pages=200,  # Limit total pages
            filter_chain=filter_chain,
            url_scorer=product_scorer,
        )

        return CrawlerRunConfig(
            deep_crawl_strategy=deep_crawl_strategy,
            scraping_strategy=LXMLWebScrapingStrategy(),
            cache_mode=CacheMode.BYPASS,
            wait_for="css:body",
            wait_until="domcontentloaded",
            page_timeout=30000,
            delay_before_return_html=2,
            stream=True,  # Enable streaming for better performance
            verbose=True,
            js_code=[
                """
                (async () => {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    // Scroll to load lazy-loaded content
                    window.scrollTo(0, document.body.scrollHeight);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    window.scrollTo(0, 0);
                })();
                """
            ],
        )

    async def process_crawl_result(self, result):
        """Process a single crawl result and extract product information."""
        if not result.success:
            return None

        # Check if this is a product page or category page with products
        is_product_page = any(pattern in result.url for pattern in [
            "/shop/product/", 
            "/product/", 
            "/pdp/",
            "/item/",
            "/detail/"
        ])
        
        is_category_page = "/shop/aisles/" in result.url
        
        if is_product_page or is_category_page:
            print(f"📦 Processing page: {result.url}")

            # Extract product information using our schema
            config = self.get_product_extraction_config()

            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                product_result = await crawler.arun(url=result.url, config=config)

                if product_result.success:
                    try:
                        extracted_data = json.loads(product_result.extracted_content)
                        if extracted_data and len(extracted_data) > 0:
                            product_data = extracted_data[0]

                            # Clean up the data
                            if (
                                "product_description" in product_data
                                and "cookie"
                                in product_data["product_description"].lower()
                            ):
                                product_data["product_description"] = (
                                    "Product description not available"
                                )

                            # Add URL and metadata
                            product_data["product_url"] = result.url
                            product_data["crawl_depth"] = result.metadata.get(
                                "depth", 0
                            )
                            product_data["crawl_score"] = result.metadata.get(
                                "score", 0
                            )

                            # Convert relative image URLs to absolute
                            if (
                                "product_image" in product_data
                                and product_data["product_image"]
                            ):
                                if not product_data["product_image"].startswith("http"):
                                    product_data["product_image"] = urljoin(
                                        result.url, product_data["product_image"]
                                    )

                            # Only return if we have meaningful product data
                            if product_data.get("product_name") or product_data.get("product_price"):
                                return product_data
                    except json.JSONDecodeError:
                        pass
        else:
            # Only log non-product pages occasionally to reduce noise
            if result.metadata.get("depth", 0) == 0 or result.metadata.get("score", 0) > 0.5:
                print(
                    f"🔍 Crawled page: {result.url} (depth: {result.metadata.get('depth', 0)}, score: {result.metadata.get('score', 0):.2f})"
                )

        return None

    async def run_deep_crawl(
        self,
        start_url: str = "https://www.safeway.com/shop/aisles/frozen-foods/ice-cream-novelties.html",
    ):
        """Run deep crawling using Crawl4AI's Best-First strategy."""
        print("🚀 Starting Deep Crawl of Safeway using BestFirstCrawlingStrategy")
        print("=" * 70)

        start_time = time.time()
        config = self.get_deep_crawl_config()

        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                print(f"🔍 Starting crawl from: {start_url}")
                print(f"📊 Max pages: {config.deep_crawl_strategy.max_pages}")
                print(f"🌳 Max depth: {config.deep_crawl_strategy.max_depth}")
                print("=" * 70)

                # Use streaming for better performance and real-time processing
                async for result in await crawler.arun(start_url, config=config):
                    product_data = await self.process_crawl_result(result)

                    if product_data:
                        self.scraped_products.append(product_data)
                        print(
                            f"   ✅ Scraped: {product_data.get('product_name', 'Unknown Product')} - {product_data.get('product_price', 'N/A')}"
                        )

                        if len(self.scraped_products) >= self.max_products:
                            print(
                                f"\n🎯 Reached target of {self.max_products} products!"
                            )
                            break

                print(
                    f"\n✅ Deep crawl completed. Found {len(self.scraped_products)} products"
                )

        except Exception as e:
            print(f"❌ Error during deep crawling: {e}")

        # Save results
        output_data = {
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_products": len(self.scraped_products),
            "crawl_config": {
                "max_pages": config.deep_crawl_strategy.max_pages,
                "max_depth": config.deep_crawl_strategy.max_depth,
                "strategy": "BestFirstCrawlingStrategy",
            },
            "products": self.scraped_products,
        }

        with open("safeway_result.json", "w") as f:
            json.dump(output_data, f, indent=2)

        end_time = time.time()
        print(f"\n🎉 Scraping completed in {end_time - start_time:.2f} seconds!")
        print(f"📊 Total products scraped: {len(self.scraped_products)}")
        print(f"💾 Results saved to safeway_result.json")

        # Print summary
        if self.scraped_products:
            print(f"\n📋 Sample products:")
            for i, product in enumerate(self.scraped_products[:5]):
                print(
                    f"   {i+1}. {product.get('product_name', 'Unknown')} - {product.get('product_price', 'N/A')} (depth: {product.get('crawl_depth', 0)})"
                )
            if len(self.scraped_products) > 5:
                print(f"   ... and {len(self.scraped_products) - 5} more products")

    async def run(
        self,
        start_url: str = "https://www.safeway.com/shop/aisles/frozen-foods/ice-cream-novelties.html",
    ):
        """Main method to run the scraper."""
        await self.run_deep_crawl(start_url) 
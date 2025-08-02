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
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import (
    ContentTypeFilter,
    DomainFilter,
    FilterChain,
    URLPatternFilter,
)
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer


class StopAndShopScraper:
    def __init__(self, max_products: int = 100, max_concurrent: int = 5):
        self.max_products = max_products
        self.max_concurrent = max_concurrent
        self.scraped_products = []

        # Browser configuration with enhanced anti-detection measures
        self.browser_config = BrowserConfig(
            headless=True,
            java_script_enabled=True,
            verbose=False,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "max-age=0",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            },
            # Additional anti-detection measures
            extra_args=[
                "--disable-blink-features=AutomationControlled",
                "--exclude-switches=enable-automation",
                "--disable-extensions-except",
                "--disable-plugins-discovery",
                "--no-first-run",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-translate",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-device-discovery-notifications",
                "--disable-web-security",
                "--allow-running-insecure-content",
            ],
        )

    def get_product_extraction_config(self):
        """Get configuration for product page extraction."""
        # Define schema for product extraction adapted for Stop and Shop
        schema = {
            "name": "Stop and Shop Product",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "product_name",
                    "selector": "h1, .product-title, [data-testid='product-title'], .product-name, .product-header h1, .product-details h1, .product-info h1, .pdp-product-name, .kds-Text--l",
                    "type": "text",
                },
                {
                    "name": "product_price",
                    "selector": ".price, .product-price, [data-testid='price'], .price-value, span[class*='price'], .product-price span, .price-display, .product-cost, .current-price, .sale-price, .kds-Price, .price-current",
                    "type": "text",
                },
                {
                    "name": "product_description",
                    "selector": ".product-description, .description, [data-testid='description'], .product-details, .product-info, .product-summary, .product-overview, .pdp-description, .product-detail-description",
                    "type": "text",
                },
                {
                    "name": "ingredients",
                    "selector": ".ingredients, .ingredient-list, [data-testid='ingredients'], .product-ingredients, .ingredients-list, .ingredient-info, .nutrition-ingredients, .pdp-ingredients",
                    "type": "text",
                },
                {
                    "name": "nutritional_info",
                    "selector": ".nutrition, .nutritional-info, [data-testid='nutrition'], .product-nutrition, .nutrition-facts, .nutrition-label, .nutrition-panel, .pdp-nutrition",
                    "type": "text",
                },
                {
                    "name": "product_image",
                    "selector": ".product-image img, .product-photo img, [data-testid='product-image'] img, .product-gallery img, img[alt*='product'], .product-hero img, .main-image img, .pdp-image img, .hero-image img",
                    "type": "attribute",
                    "attribute": "src",
                },
                {
                    "name": "product_id",
                    "selector": ".product-id, .sku, [data-testid='sku'], .product-sku, .item-number, .product-code, .upc",
                    "type": "text",
                },
                {
                    "name": "brand",
                    "selector": ".brand, .product-brand, .brand-name, [data-testid='brand'], .manufacturer, .product-manufacturer",
                    "type": "text",
                },
                {
                    "name": "unit_size",
                    "selector": ".unit-size, .package-size, .size, .weight, .volume, .product-size, [data-testid='size']",
                    "type": "text",
                },
                {
                    "name": "availability",
                    "selector": ".availability, .stock-status, .in-stock, .out-of-stock, [data-testid='availability'], .product-availability",
                    "type": "text",
                },
            ],
        }

        extraction_strategy = JsonCssExtractionStrategy(schema, verbose=False)

        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_for="css:body",
            wait_until="networkidle",
            page_timeout=45000,
            delay_before_return_html=5,
            extraction_strategy=extraction_strategy,
            js_code=[
                """
                (async () => {
                    // Hide automation indicators
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Remove automation properties
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                    
                    // Human-like delay with randomization
                    const humanDelay = (min, max) => new Promise(resolve => 
                        setTimeout(resolve, Math.random() * (max - min) + min)
                    );
                    
                    // Simulate human mouse movement
                    const simulateMouseMovement = () => {
                        const event = new MouseEvent('mousemove', {
                            clientX: Math.random() * window.innerWidth,
                            clientY: Math.random() * window.innerHeight
                        });
                        document.dispatchEvent(event);
                    };
                    
                    // Wait for page to load with human-like delay
                    await humanDelay(2000, 4000);
                    
                    // Simulate some mouse movement
                    for (let i = 0; i < 3; i++) {
                        simulateMouseMovement();
                        await humanDelay(500, 1000);
                    }
                    
                    // Handle security/privacy dialogs
                    const dialogSelectors = [
                        '.save-preference-btn-handler.onetrust-close-btn-handler',
                        '.onetrust-close-btn-handler',
                        '.save-preference-btn-handler',
                        '#onetrust-accept-btn-handler',
                        '.onetrust-accept-btn-handler',
                        'button[title="Confirm My Choices"]',
                        'button:contains("Accept")',
                        'button:contains("Continue")',
                        'button:contains("Proceed")'
                    ];
                    
                    // Try to handle dialogs multiple times
                    for (let attempt = 0; attempt < 3; attempt++) {
                        await humanDelay(1000, 2000);
                        
                        for (const selector of dialogSelectors) {
                            try {
                                const button = document.querySelector(selector);
                                if (button && button.offsetParent !== null) {
                                    // Simulate human click behavior
                                    button.focus();
                                    await humanDelay(100, 300);
                                    button.click();
                                    await humanDelay(2000, 3000);
                                    break;
                                }
                            } catch (e) {
                                // Silent error handling
                            }
                        }
                        
                        // Also try text-based button selection
                        const buttons = document.querySelectorAll('button');
                        for (const button of buttons) {
                            if (button.textContent && (
                                button.textContent.includes('Confirm') ||
                                button.textContent.includes('Accept') ||
                                button.textContent.includes('Continue') ||
                                button.textContent.includes('Proceed')
                            )) {
                                button.focus();
                                await humanDelay(100, 300);
                                button.click();
                                await humanDelay(2000, 3000);
                                break;
                            }
                        }
                    }
                    
                    // Human-like scrolling behavior
                    const scrollHeight = document.body.scrollHeight;
                    const viewportHeight = window.innerHeight;
                    let currentScroll = 0;
                    
                    // Scroll down slowly in chunks
                    while (currentScroll < scrollHeight - viewportHeight) {
                        currentScroll += Math.random() * 300 + 200;
                        window.scrollTo(0, currentScroll);
                        await humanDelay(500, 1000);
                        simulateMouseMovement();
                    }
                    
                    // Scroll back to top slowly
                    while (currentScroll > 0) {
                        currentScroll -= Math.random() * 400 + 300;
                        window.scrollTo(0, Math.max(0, currentScroll));
                        await humanDelay(300, 700);
                    }
                    
                    // Final wait
                    await humanDelay(1000, 2000);
                })();
                """
            ],
        )

    def get_deep_crawl_config(self):
        """Get configuration for deep crawling with BFS strategy."""
        # Create filter chain to focus on product pages
        filter_chain = FilterChain(
            [
                # Only crawl Stop and Shop domain
                DomainFilter(allowed_domains=["stopandshop.com"]),
                # Focus on product pages and category pages
                URLPatternFilter(
                    patterns=[
                        "*/product/*",  # Product detail pages
                        "*/products/*",  # Product listing pages
                        "*/category/*",  # Category pages
                        "*/departments/*",  # Department pages
                        "*/browse/*",  # Browse pages
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
                "grocery",
                "fresh",
                "produce",
            ],
            weight=0.8,
        )

        # Use BFS strategy for comprehensive coverage
        deep_crawl_strategy = BFSDeepCrawlStrategy(
            max_depth=3,  # Crawl 3 levels deep
            include_external=False,  # Stay within Stop and Shop domain
            max_pages=200,  # Limit total pages to crawl
            filter_chain=filter_chain,
            url_scorer=product_scorer,
            score_threshold=0.1,  # Minimum score to crawl
        )

        return CrawlerRunConfig(
            deep_crawl_strategy=deep_crawl_strategy,
            scraping_strategy=LXMLWebScrapingStrategy(),
            cache_mode=CacheMode.BYPASS,
            wait_for="css:body",
            wait_until="networkidle",
            page_timeout=30000,
            delay_before_return_html=2,
            stream=True,  # Enable streaming for better performance
            verbose=True,
            js_code=[
                """
                (async () => {
                    await new Promise(resolve => setTimeout(resolve, 2000));
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

        # Check if this is a product page
        if "/product/" in result.url:
            print(f"📦 Processing product page: {result.url}")

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

                            return product_data
                    except json.JSONDecodeError:
                        pass
        else:
            print(
                f"🔍 Crawled page: {result.url} (depth: {result.metadata.get('depth', 0)}, score: {result.metadata.get('score', 0):.2f})"
            )

        return None

    async def run_deep_crawl(
        self,
        start_url: str = "https://stopandshop.com/departments/produce",
    ):
        """Run deep crawling using Crawl4AI's built-in BFS strategy."""
        print("🚀 Starting Deep Crawl of Stop and Shop using BFSDeepCrawlStrategy")
        print("=" * 70)

        start_time = time.time()
        config = self.get_deep_crawl_config()

        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                print(f"🔍 Starting crawl from: {start_url}")
                print(f"📊 Max pages: {config.deep_crawl_strategy.max_pages}")
                print(f"🌳 Max depth: {config.deep_crawl_strategy.max_depth}")
                print("=" * 70)

                # Process results as they stream in
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
                "strategy": "BFSDeepCrawlStrategy",
            },
            "products": self.scraped_products,
        }

        with open("stopandshop_result.json", "w") as f:
            json.dump(output_data, f, indent=2)

        end_time = time.time()
        print(f"\n🎉 Scraping completed in {end_time - start_time:.2f} seconds!")
        print(f"📊 Total products scraped: {len(self.scraped_products)}")
        print(f"💾 Results saved to stopandshop_result.json")

        # Print summary
        if self.scraped_products:
            print(f"\n📋 Sample products:")
            for i, product in enumerate(self.scraped_products[:5]):
                print(
                    f"   {i+1}. {product.get('product_name', 'Unknown')} - {product.get('product_price', 'N/A')} (depth: {product.get('crawl_depth', 0)})"
                )
            if len(self.scraped_products) > 5:
                print(f"   ... and {len(self.scraped_products) - 5} more products")

    async def run_single_product(self, product_url: str):
        """Run scraper on a single product URL for testing."""
        print("🚀 Testing Stop and Shop Single Product Scraper")
        print("=" * 70)
        print(f"🔍 Target URL: {product_url}")
        print("=" * 70)

        start_time = time.time()
        config = self.get_product_extraction_config()

        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                result = await crawler.arun(url=product_url, config=config)

                if result.success:
                    try:
                        extracted_data = json.loads(result.extracted_content)
                        if extracted_data and len(extracted_data) > 0:
                            product_data = extracted_data[0]

                            # Add URL
                            product_data["product_url"] = product_url

                            # Convert relative image URLs to absolute
                            if (
                                "product_image" in product_data
                                and product_data["product_image"]
                            ):
                                if not product_data["product_image"].startswith("http"):
                                    product_data["product_image"] = urljoin(
                                        product_url, product_data["product_image"]
                                    )

                            self.scraped_products.append(product_data)
                            print(f"✅ Successfully scraped product:")
                            print(f"   Name: {product_data.get('product_name', 'N/A')}")
                            print(
                                f"   Price: {product_data.get('product_price', 'N/A')}"
                            )
                            print(f"   Brand: {product_data.get('brand', 'N/A')}")
                            print(f"   Size: {product_data.get('unit_size', 'N/A')}")

                        else:
                            print("❌ No product data extracted")
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parsing extracted data: {e}")
                else:
                    print(f"❌ Failed to crawl page: {result.error_message}")

        except Exception as e:
            print(f"❌ Error during crawling: {e}")

        # Save results
        output_data = {
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_products": len(self.scraped_products),
            "test_url": product_url,
            "products": self.scraped_products,
        }

        with open("stopandshop_single_result.json", "w") as f:
            json.dump(output_data, f, indent=2)

        end_time = time.time()
        print(
            f"\n🎉 Single product test completed in {end_time - start_time:.2f} seconds!"
        )
        print(f"💾 Results saved to stopandshop_single_result.json")

    async def run(
        self,
        start_url: str = "https://stopandshop.com/departments/produce",
        single_product_url: str = None,
    ):
        """Main method to run the scraper."""
        if single_product_url:
            await self.run_single_product(single_product_url)
        else:
            await self.run_deep_crawl(start_url)

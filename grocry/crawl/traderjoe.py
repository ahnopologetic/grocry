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


class TraderJoesScraper:
    def __init__(
        self,
        max_products: int = 100,
        max_concurrent: int = 5,
        target_file: str = "result.json",
    ):
        self.max_products = max_products
        self.max_concurrent = max_concurrent
        self.scraped_products = []
        self.target_file = target_file
        print(f"Saving results to {target_file}")

        # Browser configuration
        self.browser_config = BrowserConfig(
            headless=True, java_script_enabled=True, verbose=False
        )

    def get_product_extraction_config(self):
        """Get configuration for product page extraction."""
        # Define schema for product extraction
        schema = {
            "name": "Trader Joe's Product",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "product_name",
                    "selector": "h1, .product-title, [data-testid='product-title'], .product-name, .product-header h1, .product-details h1, .product-info h1",
                    "type": "text",
                },
                {
                    "name": "product_price",
                    "selector": ".price, .product-price, [data-testid='price'], .price-value, span[class*='price'], .product-price span, .price-display, .product-cost",
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
                    "name": "product_thumbnail_image_url",
                    "selector": ".ProductDetails_main__imageWrap__1lZIo img, .HeroImage_heroImage__image__1O61B img, .Carousel_heroImage__33Rxb img, .HeroImage_heroImage__2ugCl img, picture.HeroImage_heroImage__image__1O61B img",
                    "type": "attribute",
                    "attribute": "srcoriginal",
                },
                {
                    "name": "product_id",
                    "selector": ".product-id, .sku, [data-testid='sku'], .product-sku, .item-number",
                    "type": "text",
                },
            ],
        }

        extraction_strategy = JsonCssExtractionStrategy(schema, verbose=False)

        return CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_for="css:body",
            wait_until="networkidle",
            page_timeout=30000,
            delay_before_return_html=2,
            extraction_strategy=extraction_strategy,
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

    def get_deep_crawl_config(self):
        """Get configuration for deep crawling with BFS strategy."""
        # Create filter chain to focus on product pages
        filter_chain = FilterChain(
            [
                # Only crawl Trader Joe's domain
                DomainFilter(allowed_domains=["traderjoes.com"]),
                # Focus on product pages and category pages
                URLPatternFilter(
                    patterns=[
                        "*products/pdp/*",  # Product detail pages
                        "*products/category/*",  # Category pages
                        "*products*",  # Any product-related pages
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
            ],
            weight=0.8,
        )

        # Use BFS strategy for comprehensive coverage
        deep_crawl_strategy = BFSDeepCrawlStrategy(
            max_depth=3,  # Crawl 3 levels deep
            include_external=False,  # Stay within Trader Joe's domain
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
        if "/home/products/pdp/" in result.url:
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
                            
                            # Convert relative thumbnail URLs to absolute
                            if (
                                "product_thumbnail_image_url" in product_data
                                and product_data["product_thumbnail_image_url"]
                            ):
                                if not product_data["product_thumbnail_image_url"].startswith("http"):
                                    product_data["product_thumbnail_image_url"] = urljoin(
                                        result.url, product_data["product_thumbnail_image_url"]
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
        start_url: str = "https://www.traderjoes.com/home/products/category/food-8",
    ):
        """Run deep crawling using Crawl4AI's built-in BFS strategy."""
        print("🚀 Starting Deep Crawl of Trader Joe's using BFSDeepCrawlStrategy")
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

        with open(self.target_file, "w") as f:
            json.dump(output_data, f, indent=2)

        end_time = time.time()
        print(f"\n🎉 Scraping completed in {end_time - start_time:.2f} seconds!")
        print(f"📊 Total products scraped: {len(self.scraped_products)}")
        print(f"💾 Results saved to result.json")

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
        start_url: str = "https://www.traderjoes.com/home/products/category/food-8",
    ):
        """Main method to run the scraper."""
        await self.run_deep_crawl(start_url)

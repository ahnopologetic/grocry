import argparse
import asyncio

from grocry.crawl.traderjoe import TraderJoesScraper


async def main(url: str = None, target_file: str = "result.json"):
    if not url:
        url = "https://www.traderjoes.com/home/products/category/products-2"

    scraper = TraderJoesScraper(
        max_products=1, max_concurrent=5, target_file=target_file
    )
    await scraper.run(start_url=url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to crawl")
    parser.add_argument("--target-file", help="Target file to save results")
    args = parser.parse_args()

    asyncio.run(main(args.url, args.target_file))

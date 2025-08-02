import asyncio
from typing import List

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from grocry.api.db import get_db, init_db, Product as DbProduct
from grocry.crawl.core.db import save_products
from grocry.crawl.traderjoe import TraderJoesScraper

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


class Product(BaseModel):
    name: str
    price: float
    url: str


@app.get("/products-matching-price", response_model=List[Product])
async def products_matching_price(
    price: float,
    max_products: int = 10,
    db: Session = Depends(get_db),
):
    """
    Return products ordered by absolute difference to the given price (closest first).
    """
    from sqlalchemy import func

    # Order by absolute difference to the target price, then by price ascending
    stmt = (
        select(DbProduct)
        .where(DbProduct.price <= price)
        .order_by(func.abs(DbProduct.price - price), DbProduct.price)
        .limit(max_products)
    )
    result = db.execute(stmt)
    products = result.scalars().all()
    return [
        Product(name=product.name, price=product.price, url=product.url)
        for product in products
    ]


@app.post("/crawl-traderjoes")
async def crawl_traderjoes(
    url: str,
    max_products: int = 1000,
    max_concurrent: int = 5,
    target_file: str = "result-beverage.json",
):
    async def run_and_save():
        scraper = TraderJoesScraper(
            max_products=max_products,
            max_concurrent=max_concurrent,
            target_file=target_file,
        )
        scraper.run(start_url=url)

        save_products(target_file)

    asyncio.create_task(run_and_save())
    return {"message": "Crawling started"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

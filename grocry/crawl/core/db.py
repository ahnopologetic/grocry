import argparse
import json
from grocry.api.db import Product, get_db
from sqlalchemy import select


def save_products(json_path: str):
    """
    Save products to the database from a JSON file using the @result.json schema.
    If a product with the same name already exists, it will be skipped.
    Uses bulk insert for efficiency.
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    products = data.get("products", [])
    db = next(get_db())

    # Gather all product names from the JSON
    product_names = [
        product.get("product_name")
        for product in products
        if product.get("product_name")
    ]

    # Query existing product names in the database
    existing_names = set(
        name
        for (name,) in db.execute(
            select(Product.name).where(Product.name.in_(product_names))
        ).all()
    )

    # Prepare new Product objects, skipping duplicates
    new_products = []
    for product in products:
        name = product.get("product_name")
        if not name or name in existing_names:
            continue
        try:
            price = float(product.get("product_price").strip("$"))
        except (ValueError, AttributeError):
            continue  # Skip if price is invalid

        new_products.append(
            Product(
                name=name,
                price=price,
                url=product.get("product_url"),
                category=product.get("category"),
                store=product.get("store"),
            )
        )

    if new_products:
        db.bulk_save_objects(new_products)
        db.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="File to save products", default="result.json")
    args = parser.parse_args()
    save_products(args.file)

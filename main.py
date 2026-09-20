from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Product
from schemas import ProductCreate, ProductResponse
import math


app = FastAPI(
    title="ShopSphere API",
    description="E-commerce Backend API for ShopSphere",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==================================================
# DATABASE
# ==================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():
    return {
        "message": "Welcome to ShopSphere API",
        "status": "Backend is running"
    }


# ==================================================
# CREATE PRODUCT
# ==================================================

@app.post(
    "/products",
    response_model=ProductResponse
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category=product.category
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# ==================================================
# GET ALL PRODUCTS
# ==================================================
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully",
        "product_id": product_id
    }
# ==================================================
# UPDATE PRODUCT
# ==================================================

@app.put(
    "/products/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):

    existing_product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.stock = product.stock
    existing_product.category = product.category

    db.commit()
    db.refresh(existing_product)

    return existing_product

@app.get(
    "/products",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    return products


# ==================================================
# FILTER PRODUCTS
# ==================================================

@app.get("/products/filter")
def filter_products(
    name: str = "",
    min_price: float = 0,
    max_price: float = 999999999,
    db: Session = Depends(get_db)
):

    query = db.query(Product)

    if name:
        query = query.filter(
            Product.name.ilike(f"%{name}%")
        )

    query = query.filter(
        Product.price >= min_price
    )

    query = query.filter(
        Product.price <= max_price
    )

    products = query.all()

    return {
        "total_products": len(products),
        "filters": {
            "name": name,
            "min_price": min_price,
            "max_price": max_price
        },
        "products": products
    }


# ==================================================
# SEARCH PRODUCTS
# ==================================================

@app.get("/products/search")
def search_products(
    keyword: str,
    db: Session = Depends(get_db)
):

    products = db.query(Product).filter(
        Product.name.ilike(f"%{keyword}%")
    ).all()

    return {
        "keyword": keyword,
        "total_products": len(products),
        "products": products
    }


# ==================================================
# BROWSE PRODUCTS
# ==================================================

@app.get("/products/browse")
def browse_products(
    page: int = 1,
    limit: int = 10,
    sort: str = "name_asc",
    db: Session = Depends(get_db)
):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than 0"
        )

    query = db.query(Product)

    total_products = query.count()

    total_pages = math.ceil(
        total_products / limit
    ) if total_products > 0 else 0

    if total_products > 0 and page > total_pages:
        raise HTTPException(
            status_code=400,
            detail="Page number exceeds total pages"
        )

    if sort == "name_asc":
        query = query.order_by(Product.name.asc())

    elif sort == "name_desc":
        query = query.order_by(Product.name.desc())

    elif sort == "price_asc":
        query = query.order_by(Product.price.asc())

    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())

    elif sort == "stock_asc":
        query = query.order_by(Product.stock.asc())

    elif sort == "stock_desc":
        query = query.order_by(Product.stock.desc())

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort option"
        )

    offset = (page - 1) * limit

    products = query.offset(offset).limit(limit).all()

    return {
        "products": products,

        "pagination": {
            "current_page": page,
            "limit": limit,
            "total_products": total_products,
            "total_pages": total_pages,
            "has_next_page": page < total_pages,
            "has_previous_page": page > 1
        },

        "sorting": {
            "sort": sort
        }
    }


# ==================================================
# BROWSE INFO
# ==================================================

@app.get("/products/browse-info")
def browse_info(
    page: int = 1,
    limit: int = 10,
    sort: str = "name_asc",
    db: Session = Depends(get_db)
):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than 0"
        )

    total_products = db.query(Product).count()

    total_pages = math.ceil(
        total_products / limit
    ) if total_products > 0 else 0

    return {
        "pagination": {
            "current_page": page,
            "limit": limit,
            "total_products": total_products,
            "total_pages": total_pages,
            "has_next_page": page < total_pages,
            "has_previous_page": page > 1
        },

        "sorting_options": [
            "name_asc",
            "name_desc",
            "price_asc",
            "price_desc",
            "stock_asc",
            "stock_desc"
        ],

        "current_sort": sort
    }


# ==================================================
# CATEGORY PRODUCTS
# ==================================================

@app.get("/products/category/{category_name}")
def get_products_by_category(
    category_name: str,
    db: Session = Depends(get_db)
):

    products = db.query(Product).filter(
        Product.category.ilike(category_name)
    ).all()

    return {
        "category": category_name,
        "total_products": len(products),
        "products": products
    }


# ==================================================
# ADVANCED BROWSE
# ==================================================

@app.get("/products/advanced-browse")
def advanced_browse(
    page: int = 1,
    limit: int = 10,
    category: str = "",
    min_price: float = 0,
    max_price: float = 999999999,
    min_stock: int = 0,
    sort: str = "name_asc",
    db: Session = Depends(get_db)
):

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be greater than 0"
        )

    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be greater than 0"
        )

    query = db.query(Product)

    if category:
        query = query.filter(
            Product.category.ilike(category)
        )

    query = query.filter(
        Product.price >= min_price
    )

    query = query.filter(
        Product.price <= max_price
    )

    query = query.filter(
        Product.stock >= min_stock
    )

    total_products = query.count()

    total_pages = math.ceil(
        total_products / limit
    ) if total_products > 0 else 0

    if sort == "name_asc":
        query = query.order_by(Product.name.asc())

    elif sort == "name_desc":
        query = query.order_by(Product.name.desc())

    elif sort == "price_asc":
        query = query.order_by(Product.price.asc())

    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())

    elif sort == "stock_asc":
        query = query.order_by(Product.stock.asc())

    elif sort == "stock_desc":
        query = query.order_by(Product.stock.desc())

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort option"
        )

    offset = (page - 1) * limit

    products = query.offset(offset).limit(limit).all()

    return {
        "products": products,

        "pagination": {
            "current_page": page,
            "limit": limit,
            "total_products": total_products,
            "total_pages": total_pages,
            "has_next_page": page < total_pages,
            "has_previous_page": page > 1
        },

        "filters": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "min_stock": min_stock
        },

        "sorting": {
            "sort": sort
        }
    }


# ==================================================
# LOW STOCK
# ==================================================

@app.get("/products/low-stock")
def get_low_stock_products(
    threshold: int = 5,
    db: Session = Depends(get_db)
):

    products = db.query(Product).filter(
        Product.stock <= threshold
    ).all()

    return {
        "threshold": threshold,
        "total_products": len(products),
        "products": products
    }


# ==================================================
# OUT OF STOCK
# ==================================================

@app.get("/products/out-of-stock")
def get_out_of_stock_products(
    db: Session = Depends(get_db)
):

    products = db.query(Product).filter(
        Product.stock == 0
    ).all()

    return {
        "total_products": len(products),
        "products": products
    }


# ==================================================
# STOCK SUMMARY
# ==================================================

@app.get("/products/stock-summary")
def get_stock_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_stock_quantity = sum(
        product.stock
        for product in products
    )

    low_stock_products = sum(
        1
        for product in products
        if product.stock <= 5
    )

    out_of_stock_products = sum(
        1
        for product in products
        if product.stock == 0
    )

    return {
        "total_products": len(products),
        "total_stock_quantity": total_stock_quantity,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products
    }


# ==================================================
# INVENTORY VALUE
# ==================================================

@app.get("/products/inventory-value")
def get_inventory_value(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    return {
        "total_products": len(products),
        "total_inventory_value": total_inventory_value
    }


# ==================================================
# INVENTORY VALUE BY CATEGORY
# ==================================================

@app.get("/products/inventory-value/category")
def get_inventory_value_by_category(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    category_values = {}

    for product in products:

        category = product.category or "Uncategorized"

        stock_value = (
            product.price *
            product.stock
        )

        if category not in category_values:
            category_values[category] = 0

        category_values[category] += stock_value

    return {
        "categories": category_values
    }


# ==================================================
# CATEGORY SUMMARY
# ==================================================

@app.get("/products/category-summary")
def get_category_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    category_summary = {}

    for product in products:

        category = product.category or "Uncategorized"

        if category not in category_summary:
            category_summary[category] = {
                "product_count": 0,
                "total_stock": 0,
                "total_stock_value": 0
            }

        category_summary[category]["product_count"] += 1

        category_summary[category]["total_stock"] += (
            product.stock
        )

        category_summary[category]["total_stock_value"] += (
            product.price *
            product.stock
        )

    return {
        "categories": category_summary
    }


# ==================================================
# PRICE STATISTICS
# ==================================================

@app.get("/products/price-statistics")
def get_price_statistics(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "minimum_price": 0,
            "maximum_price": 0,
            "average_price": 0
        }

    prices = [
        product.price
        for product in products
    ]

    return {
        "total_products": len(products),
        "minimum_price": min(prices),
        "maximum_price": max(prices),
        "average_price": round(
            sum(prices) / len(prices),
            2
        )
    }


# ==================================================
# STEP 6.17 — STOCK VALUE STATISTICS
# ==================================================

@app.get("/products/stock-value-statistics")
def get_stock_value_statistics(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "total_stock_quantity": 0,
            "total_stock_value": 0,
            "average_stock_value_per_product": 0,
            "highest_value_product": None,
            "lowest_value_product": None
        }

    total_stock_quantity = sum(
        product.stock
        for product in products
    )

    total_stock_value = sum(
        product.price * product.stock
        for product in products
    )

    average_stock_value = (
        total_stock_value / len(products)
    )

    highest_product = max(
        products,
        key=lambda product: product.price * product.stock
    )

    lowest_product = min(
        products,
        key=lambda product: product.price * product.stock
    )

    return {
        "total_products": len(products),
        "total_stock_quantity": total_stock_quantity,
        "total_stock_value": total_stock_value,
        "average_stock_value_per_product": round(
            average_stock_value,
            2
        ),
        "highest_value_product": {
            "product_id": highest_product.id,
            "product_name": highest_product.name,
            "price": highest_product.price,
            "stock": highest_product.stock,
            "stock_value": (
                highest_product.price *
                highest_product.stock
            )
        },
        "lowest_value_product": {
            "product_id": lowest_product.id,
            "product_name": lowest_product.name,
            "price": lowest_product.price,
            "stock": lowest_product.stock,
            "stock_value": (
                lowest_product.price *
                lowest_product.stock
            )
        }
    }


# ==================================================
# STEP 6.18 — STOCK VALUE RANKING
# ==================================================

@app.get("/products/stock-value-ranking")
def get_stock_value_ranking(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    ranking = []

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        ranking.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value
        })

    ranking.sort(
        key=lambda product: product["stock_value"],
        reverse=True
    )

    ranked_products = []

    for rank, product in enumerate(
        ranking,
        start=1
    ):

        ranked_products.append({
            "rank": rank,
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "price": product["price"],
            "stock": product["stock"],
            "stock_value": product["stock_value"]
        })

    return {
        "total_products": len(ranked_products),
        "products": ranked_products
    }


# ==================================================
# STEP 6.19 — STOCK VALUE PERCENTAGE
# ==================================================

@app.get("/products/stock-value-percentage")
def get_stock_value_percentage(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "total_stock_value": 0,
            "products": []
        }

    total_stock_value = sum(
        product.price * product.stock
        for product in products
    )

    percentage_products = []

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        if total_stock_value > 0:
            percentage = (
                stock_value /
                total_stock_value
            ) * 100
        else:
            percentage = 0

        percentage_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "stock_value_percentage": round(
                percentage,
                2
            )
        })

    percentage_products.sort(
        key=lambda product:
        product["stock_value_percentage"],
        reverse=True
    )

    return {
        "total_products": len(percentage_products),
        "total_stock_value": total_stock_value,
        "products": percentage_products
    }


# ==================================================
# STEP 6.20 — STOCK VALUE CONTRIBUTION
# ==================================================

@app.get("/products/stock-value-contribution")
def get_stock_value_contribution(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "total_stock_value": 0,
            "products": []
        }

    total_stock_value = sum(
        product.price *
        product.stock
        for product in products
    )

    contribution_products = []

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        if total_stock_value > 0:
            contribution_percentage = (
                stock_value /
                total_stock_value
            ) * 100
        else:
            contribution_percentage = 0

        contribution_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "contribution_percentage": round(
                contribution_percentage,
                2
            )
        })

    contribution_products.sort(
        key=lambda product:
        product["contribution_percentage"],
        reverse=True
    )

    ranked_products = []

    for rank, product in enumerate(
        contribution_products,
        start=1
    ):

        ranked_products.append({
            "rank": rank,
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "price": product["price"],
            "stock": product["stock"],
            "stock_value": product["stock_value"],
            "contribution_percentage":
                product["contribution_percentage"]
        })

    return {
        "total_products": len(ranked_products),
        "total_stock_value": total_stock_value,
        "products": ranked_products
    }


# ==================================================
# STEP 6.21 — STOCK VALUE DISTRIBUTION
# ==================================================

@app.get("/products/stock-value-distribution")
def get_stock_value_distribution(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    high_value_products = []
    medium_value_products = []
    low_value_products = []

    high_value_total = 0
    medium_value_total = 0
    low_value_total = 0

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        if stock_value > 500000:

            high_value_products.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value
            })

            high_value_total += stock_value

        elif stock_value >= 100000:

            medium_value_products.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value
            })

            medium_value_total += stock_value

        else:

            low_value_products.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value
            })

            low_value_total += stock_value

    return {
        "total_products": len(products),

        "high_value_products": len(
            high_value_products
        ),

        "medium_value_products": len(
            medium_value_products
        ),

        "low_value_products": len(
            low_value_products
        ),

        "high_value_total": high_value_total,

        "medium_value_total": medium_value_total,

        "low_value_total": low_value_total,

        "products": {
            "high_value": high_value_products,
            "medium_value": medium_value_products,
            "low_value": low_value_products
        }
    }


# ==================================================
# STEP 6.22 — STOCK VALUE SUMMARY
# ==================================================

@app.get("/products/stock-value-summary")
def get_stock_value_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "total_stock_quantity": 0,
            "total_stock_value": 0,
            "average_stock_value_per_product": 0,
            "highest_value_product": None,
            "lowest_value_product": None
        }

    total_stock_quantity = sum(
        product.stock
        for product in products
    )

    total_stock_value = sum(
        product.price *
        product.stock
        for product in products
    )

    average_stock_value = (
        total_stock_value /
        len(products)
    )

    highest_product = max(
        products,
        key=lambda product:
        product.price *
        product.stock
    )

    lowest_product = min(
        products,
        key=lambda product:
        product.price *
        product.stock
    )

    highest_stock_value = (
        highest_product.price *
        highest_product.stock
    )

    lowest_stock_value = (
        lowest_product.price *
        lowest_product.stock
    )

    return {
        "total_products": len(products),

        "total_stock_quantity":
            total_stock_quantity,

        "total_stock_value":
            total_stock_value,

        "average_stock_value_per_product":
            round(
                average_stock_value,
                2
            ),

        "highest_value_product": {
            "product_id":
                highest_product.id,

            "product_name":
                highest_product.name,

            "price":
                highest_product.price,

            "stock":
                highest_product.stock,

            "stock_value":
                highest_stock_value
        },

        "lowest_value_product": {
            "product_id":
                lowest_product.id,

            "product_name":
                lowest_product.name,

            "price":
                lowest_product.price,

            "stock":
                lowest_product.stock,

            "stock_value":
                lowest_stock_value
        }
    }


# ==================================================
# STEP 6.23 — INVENTORY HEALTH
# ==================================================

@app.get("/products/inventory-health")
def get_inventory_health(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "healthy_products": 0,
            "low_stock_products": 0,
            "out_of_stock_products": 0,
            "inventory_health_score": 0,
            "products": []
        }

    healthy_products = 0
    low_stock_products = 0
    out_of_stock_products = 0

    health_products = []

    for product in products:

        if product.stock == 0:

            status = "Out of Stock"
            score = 0

            out_of_stock_products += 1

        elif product.stock <= 5:

            status = "Low Stock"
            score = 50

            low_stock_products += 1

        else:

            status = "Healthy"
            score = 100

            healthy_products += 1

        health_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "status": status,
            "health_score": score
        })

    total_health_score = sum(
        product["health_score"]
        for product in health_products
    )

    inventory_health_score = round(
        total_health_score /
        len(health_products),
        2
    )

    return {
        "total_products": len(products),

        "healthy_products":
            healthy_products,

        "low_stock_products":
            low_stock_products,

        "out_of_stock_products":
            out_of_stock_products,

        "inventory_health_score":
            inventory_health_score,

        "products":
            health_products
    }


# ==================================================
# STEP 6.24 — INVENTORY RISK ANALYSIS
# ==================================================

@app.get("/products/inventory-risk")
def get_inventory_risk(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "critical_products": 0,
            "high_risk_products": 0,
            "medium_risk_products": 0,
            "low_risk_products": 0,
            "overall_risk_level": "No Products",
            "products": []
        }

    critical_products = 0
    high_risk_products = 0
    medium_risk_products = 0
    low_risk_products = 0

    risk_products = []

    for product in products:

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100

            critical_products += 1

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75

            high_risk_products += 1

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50

            medium_risk_products += 1

        else:

            risk_level = "Low"
            risk_score = 0

            low_risk_products += 1

        risk_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    total_risk_score = sum(
        product["risk_score"]
        for product in risk_products
    )

    average_risk_score = (
        total_risk_score /
        len(risk_products)
    )

    if average_risk_score >= 75:
        overall_risk_level = "Critical"

    elif average_risk_score >= 50:
        overall_risk_level = "High"

    elif average_risk_score > 0:
        overall_risk_level = "Medium"

    else:
        overall_risk_level = "Low"

    risk_products.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    return {
        "total_products": len(products),

        "critical_products":
            critical_products,

        "high_risk_products":
            high_risk_products,

        "medium_risk_products":
            medium_risk_products,

        "low_risk_products":
            low_risk_products,

        "overall_risk_level":
            overall_risk_level,

        "average_risk_score":
            round(
                average_risk_score,
                2
            ),

        "products":
            risk_products
    }


# ==================================================
# STEP 6.25 — INVENTORY RISK SUMMARY
# ==================================================

@app.get("/products/inventory-risk-summary")
def get_inventory_risk_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "critical_products": 0,
            "high_risk_products": 0,
            "medium_risk_products": 0,
            "low_risk_products": 0,
            "overall_risk_level": "No Products",
            "average_risk_score": 0,
            "highest_risk_product": None,
            "lowest_risk_product": None
        }

    critical_products = 0
    high_risk_products = 0
    medium_risk_products = 0
    low_risk_products = 0

    risk_products = []

    for product in products:

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100

            critical_products += 1

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75

            high_risk_products += 1

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50

            medium_risk_products += 1

        else:

            risk_level = "Low"
            risk_score = 0

            low_risk_products += 1

        risk_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    total_risk_score = sum(
        product["risk_score"]
        for product in risk_products
    )

    average_risk_score = (
        total_risk_score /
        len(risk_products)
    )

    if average_risk_score >= 75:
        overall_risk_level = "Critical"

    elif average_risk_score >= 50:
        overall_risk_level = "High"

    elif average_risk_score > 0:
        overall_risk_level = "Medium"

    else:
        overall_risk_level = "Low"

    highest_risk_product = max(
        risk_products,
        key=lambda product:
        product["risk_score"]
    )

    lowest_risk_product = min(
        risk_products,
        key=lambda product:
        product["risk_score"]
    )

    return {
        "total_products": len(products),

        "critical_products":
            critical_products,

        "high_risk_products":
            high_risk_products,

        "medium_risk_products":
            medium_risk_products,

        "low_risk_products":
            low_risk_products,

        "overall_risk_level":
            overall_risk_level,

        "average_risk_score":
            round(
                average_risk_score,
                2
            ),

        "highest_risk_product":
            highest_risk_product,

        "lowest_risk_product":
            lowest_risk_product
    }


# ==================================================
# STEP 6.26 — INVENTORY RISK RECOMMENDATIONS
# ==================================================

@app.get("/products/inventory-risk-recommendations")
def get_inventory_risk_recommendations(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "recommendations": []
        }

    recommendations = []

    for product in products:

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            recommendation = "Restock immediately"

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            recommendation = "Restock soon"

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            recommendation = "Monitor stock"

        else:

            risk_level = "Low"
            risk_score = 0
            recommendation = "Stock level healthy"

        recommendations.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "recommendation": recommendation
        })

    recommendations.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    return {
        "total_products": len(products),
        "recommendations": recommendations
    }


# ==================================================
# STEP 6.27 — INVENTORY RISK ACTION PLAN
# ==================================================

@app.get("/products/inventory-risk-action-plan")
def get_inventory_risk_action_plan(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "action_plan": []
        }

    action_plan = []

    for product in products:

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            action = "Immediate Restock"

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            action = "Create Purchase Order"

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            action = "Monitor & Review"

        else:

            risk_level = "Low"
            risk_score = 0
            action = "No Immediate Action"

        action_plan.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "action": action
        })

    action_plan.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    return {
        "total_products": len(products),
        "action_plan": action_plan
    }


# ==================================================
# STEP 6.28 — INVENTORY DASHBOARD
# ==================================================

@app.get("/products/inventory-dashboard")
def get_inventory_dashboard(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "dashboard": {
                "total_products": 0,
                "total_stock_quantity": 0,
                "total_inventory_value": 0,
                "inventory_health_score": 0,
                "overall_risk_level": "No Products",
                "average_risk_score": 0
            },
            "stock": {
                "healthy_products": 0,
                "low_stock_products": 0,
                "out_of_stock_products": 0
            },
            "risk": {
                "critical_products": 0,
                "high_risk_products": 0,
                "medium_risk_products": 0,
                "low_risk_products": 0
            },
            "highest_value_product": None,
            "highest_risk_product": None,
            "recommendations": [],
            "action_plan": []
        }

    total_products = len(products)

    total_stock_quantity = sum(
        product.stock
        for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    healthy_products = 0
    low_stock_products = 0
    out_of_stock_products = 0

    health_scores = []

    for product in products:

        if product.stock == 0:

            out_of_stock_products += 1
            health_scores.append(0)

        elif product.stock <= 5:

            low_stock_products += 1
            health_scores.append(50)

        else:

            healthy_products += 1
            health_scores.append(100)

    inventory_health_score = round(
        sum(health_scores) /
        len(health_scores),
        2
    )

    critical_products = 0
    high_risk_products = 0
    medium_risk_products = 0
    low_risk_products = 0

    risk_products = []

    for product in products:

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            critical_products += 1

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            high_risk_products += 1

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            medium_risk_products += 1

        else:

            risk_level = "Low"
            risk_score = 0
            low_risk_products += 1

        risk_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    average_risk_score = round(
        sum(
            product["risk_score"]
            for product in risk_products
        ) / len(risk_products),
        2
    )

    if average_risk_score >= 75:

        overall_risk_level = "Critical"

    elif average_risk_score >= 50:

        overall_risk_level = "High"

    elif average_risk_score > 0:

        overall_risk_level = "Medium"

    else:

        overall_risk_level = "Low"

    highest_value_product = max(
        products,
        key=lambda product:
        product.price * product.stock
    )

    highest_value_product_data = {
        "product_id": highest_value_product.id,
        "product_name": highest_value_product.name,
        "price": highest_value_product.price,
        "stock": highest_value_product.stock,
        "stock_value": (
            highest_value_product.price *
            highest_value_product.stock
        )
    }

    risk_products.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    highest_risk_product = (
        risk_products[0]
        if risk_products
        else None
    )

    recommendations = []

    for product in products:

        if product.stock == 0:

            recommendation = "Restock immediately"

        elif product.stock <= 5:

            recommendation = "Restock soon"

        elif product.stock <= 10:

            recommendation = "Monitor stock"

        else:

            recommendation = "Stock level healthy"

        recommendations.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "recommendation": recommendation
        })

    action_plan = []

    for product in products:

        if product.stock == 0:

            action = "Immediate Restock"
            risk_score = 100

        elif product.stock <= 5:

            action = "Create Purchase Order"
            risk_score = 75

        elif product.stock <= 10:

            action = "Monitor & Review"
            risk_score = 50

        else:

            action = "No Immediate Action"
            risk_score = 0

        action_plan.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "risk_score": risk_score,
            "action": action
        })

    action_plan.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    return {
        "dashboard": {
            "total_products": total_products,
            "total_stock_quantity": total_stock_quantity,
            "total_inventory_value": total_inventory_value,
            "inventory_health_score": inventory_health_score,
            "overall_risk_level": overall_risk_level,
            "average_risk_score": average_risk_score
        },

        "stock": {
            "healthy_products": healthy_products,
            "low_stock_products": low_stock_products,
            "out_of_stock_products": out_of_stock_products
        },

        "risk": {
            "critical_products": critical_products,
            "high_risk_products": high_risk_products,
            "medium_risk_products": medium_risk_products,
            "low_risk_products": low_risk_products
        },

        "highest_value_product":
            highest_value_product_data,

        "highest_risk_product":
            highest_risk_product,

        "recommendations":
            recommendations,

        "action_plan":
            action_plan
    }


# ==================================================
# STEP 6.29 — INVENTORY DASHBOARD PRODUCT RANKING
# ==================================================

@app.get("/products/inventory-dashboard-ranking")
def get_inventory_dashboard_ranking(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "products": []
        }

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    ranking = []

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50

        else:

            risk_level = "Low"
            risk_score = 0

        if total_inventory_value > 0:

            stock_value_percentage = (
                stock_value /
                total_inventory_value
            ) * 100

        else:

            stock_value_percentage = 0

        ranking.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "stock_value_percentage": round(
                stock_value_percentage,
                2
            ),
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    ranking.sort(
        key=lambda product:
        product["stock_value"],
        reverse=True
    )

    ranked_products = []

    for rank, product in enumerate(
        ranking,
        start=1
    ):

        ranked_products.append({
            "rank": rank,
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "price": product["price"],
            "stock": product["stock"],
            "stock_value": product["stock_value"],
            "stock_value_percentage":
                product["stock_value_percentage"],
            "risk_level": product["risk_level"],
            "risk_score": product["risk_score"]
        })

    return {
        "total_products": len(ranked_products),
        "total_inventory_value": total_inventory_value,
        "products": ranked_products
    }


# ==================================================
# STEP 6.30 — INVENTORY RISK RANKING
# ==================================================

@app.get("/products/inventory-risk-ranking")
def get_inventory_risk_ranking(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "critical_products": 0,
            "high_risk_products": 0,
            "medium_risk_products": 0,
            "low_risk_products": 0,
            "products": []
        }

    critical_products = 0
    high_risk_products = 0
    medium_risk_products = 0
    low_risk_products = 0

    ranking = []

    for product in products:

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            critical_products += 1

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            high_risk_products += 1

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            medium_risk_products += 1

        else:

            risk_level = "Low"
            risk_score = 0
            low_risk_products += 1

        ranking.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    # Highest risk first.
    # If risk is same, product with lower stock comes first.
    # If stock is also same, higher price comes first.

    ranking.sort(
        key=lambda product: (
            -product["risk_score"],
            product["stock"],
            -product["price"]
        )
    )

    ranked_products = []

    for rank, product in enumerate(
        ranking,
        start=1
    ):

        ranked_products.append({
            "rank": rank,
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "price": product["price"],
            "stock": product["stock"],
            "risk_level": product["risk_level"],
            "risk_score": product["risk_score"]
        })

    total_risk_score = sum(
        product["risk_score"]
        for product in ranked_products
    )

    average_risk_score = round(
        total_risk_score /
        len(ranked_products),
        2
    )

    if average_risk_score >= 75:

        overall_risk_level = "Critical"

    elif average_risk_score >= 50:

        overall_risk_level = "High"

    elif average_risk_score > 0:

        overall_risk_level = "Medium"

    else:

        overall_risk_level = "Low"

    return {
        "total_products": len(ranked_products),

        "critical_products":
            critical_products,

        "high_risk_products":
            high_risk_products,

        "medium_risk_products":
            medium_risk_products,

        "low_risk_products":
            low_risk_products,

        "overall_risk_level":
            overall_risk_level,

        "average_risk_score":
            average_risk_score,

        "products":
            ranked_products
    }


# ==================================================
# GET PRODUCT STOCK
# ==================================================

@app.get("/products/{product_id}/stock")
def get_product_stock(
    product_id: int,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "product_id": product.id,
        "product_name": product.name,
        "stock": product.stock
    }


# ==================================================
# ADD STOCK
# ==================================================

@app.post("/products/{product_id}/stock/add")
def add_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    product.stock += quantity

    db.commit()
    db.refresh(product)

    return {
        "message": "Stock added successfully",
        "product_id": product.id,
        "product_name": product.name,
        "added_quantity": quantity,
        "new_stock": product.stock
    }


# ==================================================
# REMOVE STOCK
# ==================================================

@app.post("/products/{product_id}/stock/remove")
def remove_stock(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db)
):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    if quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock available"
        )

    product.stock -= quantity

    db.commit()
    db.refresh(product)

    return {
        "message": "Stock removed successfully",
        "product_id": product.id,
        "product_name": product.name,
        "removed_quantity": quantity,
        "new_stock": product.stock
    }
    
    # ==================================================
# STEP 6.31 — INVENTORY RISK DISTRIBUTION
# ==================================================

@app.get("/products/inventory-risk-distribution")
def get_inventory_risk_distribution(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,

            "risk_distribution": {
                "critical": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },

                "high": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },

                "medium": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },

                "low": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                }
            }
        }

    risk_distribution = {

        "critical": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        },

        "high": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        },

        "medium": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        },

        "low": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        # ------------------------------------------
        # RISK CLASSIFICATION
        # ------------------------------------------

        if product.stock == 0:

            risk_category = "critical"

        elif product.stock <= 5:

            risk_category = "high"

        elif product.stock <= 10:

            risk_category = "medium"

        else:

            risk_category = "low"

        # ------------------------------------------
        # INVENTORY VALUE
        # ------------------------------------------

        stock_value = (
            product.price *
            product.stock
        )

        # ------------------------------------------
        # UPDATE RISK DISTRIBUTION
        # ------------------------------------------

        risk_distribution[
            risk_category
        ]["product_count"] += 1

        risk_distribution[
            risk_category
        ]["total_stock"] += product.stock

        risk_distribution[
            risk_category
        ]["inventory_value"] += stock_value

    # ------------------------------------------
    # TOTAL PRODUCTS
    # ------------------------------------------

    total_products = len(products)

    # ------------------------------------------
    # CALCULATE PERCENTAGE
    # ------------------------------------------

    for category in risk_distribution:

        product_count = (
            risk_distribution[category]
            ["product_count"]
        )

        risk_distribution[category][
            "percentage"
        ] = round(
            (
                product_count /
                total_products
            ) * 100,
            2
        )

    # ------------------------------------------
    # FINAL RESPONSE
    # ------------------------------------------

    return {

        "total_products":
            total_products,

        "risk_distribution":
            risk_distribution
    }
    # ==================================================
# STEP 6.32 — INVENTORY RISK ALERTS
# ==================================================

@app.get("/products/inventory-risk-alerts")
def get_inventory_risk_alerts(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    alerts = []

    for product in products:

        # ------------------------------------------
        # RISK CLASSIFICATION
        # ------------------------------------------

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            alert = "URGENT: Product is out of stock"

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            alert = "Restock required soon"

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            alert = "Monitor stock level"

        else:

            risk_level = "Low"
            risk_score = 0
            alert = "Stock level is healthy"

        # ------------------------------------------
        # ONLY CREATE ALERTS FOR RISK PRODUCTS
        # ------------------------------------------

        if risk_level != "Low":

            inventory_value = (
                product.price *
                product.stock
            )

            alerts.append({

                "product_id":
                    product.id,

                "product_name":
                    product.name,

                "price":
                    product.price,

                "stock":
                    product.stock,

                "inventory_value":
                    inventory_value,

                "risk_level":
                    risk_level,

                "risk_score":
                    risk_score,

                "alert":
                    alert
            })

    # ------------------------------------------
    # SORT ALERTS
    # ------------------------------------------

    alerts.sort(
        key=lambda x: (
            -x["risk_score"],
            x["stock"],
            -x["inventory_value"]
        )
    )

    # ------------------------------------------
    # ALERT SUMMARY
    # ------------------------------------------

    critical_alerts = sum(
        1
        for item in alerts
        if item["risk_level"] == "Critical"
    )

    high_alerts = sum(
        1
        for item in alerts
        if item["risk_level"] == "High"
    )

    medium_alerts = sum(
        1
        for item in alerts
        if item["risk_level"] == "Medium"
    )

    # ------------------------------------------
    # OVERALL ALERT STATUS
    # ------------------------------------------

    if critical_alerts > 0:

        overall_status = "Critical"

    elif high_alerts > 0:

        overall_status = "High"

    elif medium_alerts > 0:

        overall_status = "Medium"

    else:

        overall_status = "Healthy"

    # ------------------------------------------
    # FINAL RESPONSE
    # ------------------------------------------

    return {

        "total_products":
            len(products),

        "total_alerts":
            len(alerts),

        "critical_alerts":
            critical_alerts,

        "high_alerts":
            high_alerts,

        "medium_alerts":
            medium_alerts,

        "overall_status":
            overall_status,

        "alerts":
            alerts
    } 
 
# ==================================================
# STEP 6.33 — INVENTORY RISK SUMMARY
# ==================================================

@app.get("/products/inventory-risk-summary-report")
def get_inventory_risk_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    # ------------------------------------------
    # EMPTY DATABASE
    # ------------------------------------------

    if not products:

        return {
            "total_products": 0,
            "total_stock": 0,
            "total_inventory_value": 0,

            "risk_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },

            "overall_risk": "Low",

            "recommendation":
                "No products available for analysis"
        }

    # ------------------------------------------
    # INITIAL VALUES
    # ------------------------------------------

    total_stock = 0
    total_inventory_value = 0

    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    total_risk_score = 0

    # ------------------------------------------
    # ANALYZE PRODUCTS
    # ------------------------------------------

    for product in products:

        total_stock += product.stock

        inventory_value = (
            product.price *
            product.stock
        )

        total_inventory_value += inventory_value

        # --------------------------------------
        # RISK CLASSIFICATION
        # --------------------------------------

        if product.stock == 0:

            risk_score = 100
            critical_count += 1

        elif product.stock <= 5:

            risk_score = 75
            high_count += 1

        elif product.stock <= 10:

            risk_score = 50
            medium_count += 1

        else:

            risk_score = 0
            low_count += 1

        total_risk_score += risk_score

    # ------------------------------------------
    # AVERAGE RISK SCORE
    # ------------------------------------------

    average_risk_score = round(
        total_risk_score /
        len(products),
        2
    )

    # ------------------------------------------
    # OVERALL RISK
    # ------------------------------------------

    if average_risk_score >= 75:

        overall_risk = "Critical"

    elif average_risk_score >= 50:

        overall_risk = "High"

    elif average_risk_score > 0:

        overall_risk = "Medium"

    else:

        overall_risk = "Low"

    # ------------------------------------------
    # RECOMMENDATION
    # ------------------------------------------

    if critical_count > 0:

        recommendation = (
            "Immediate restocking required "
            "for critical products"
        )

    elif high_count > 0:

        recommendation = (
            "Restock high-risk products soon"
        )

    elif medium_count > 0:

        recommendation = (
            "Monitor medium-risk products"
        )

    else:

        recommendation = (
            "Inventory levels are healthy"
        )

    # ------------------------------------------
    # FINAL RESPONSE
    # ------------------------------------------

    return {

        "total_products":
            len(products),

        "total_stock":
            total_stock,

        "total_inventory_value":
            total_inventory_value,

        "risk_summary": {

            "critical":
                critical_count,

            "high":
                high_count,

            "medium":
                medium_count,

            "low":
                low_count
        },

        "average_risk_score":
            average_risk_score,

        "overall_risk":
            overall_risk,

        "recommendation":
            recommendation
    } 
    # ==================================================
# STEP 6.34 — INVENTORY RISK REPORT
# ==================================================

@app.get("/products/inventory-risk-report")
def get_inventory_risk_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    # ------------------------------------------
    # EMPTY DATABASE
    # ------------------------------------------

    if not products:

        return {
            "total_products": 0,
            "total_stock": 0,
            "total_inventory_value": 0,

            "risk_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },

            "average_risk_score": 0,
            "overall_risk": "Low",

            "highest_risk_product": None,
            "lowest_risk_product": None,

            "alerts": [],

            "recommendation":
                "No products available for analysis"
        }

    # ------------------------------------------
    # INITIAL VALUES
    # ------------------------------------------

    total_stock = 0
    total_inventory_value = 0
    total_risk_score = 0

    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    risk_products = []
    alerts = []

    # ------------------------------------------
    # ANALYZE PRODUCTS
    # ------------------------------------------

    for product in products:

        total_stock += product.stock

        inventory_value = (
            product.price *
            product.stock
        )

        total_inventory_value += inventory_value

        # --------------------------------------
        # RISK CLASSIFICATION
        # --------------------------------------

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            critical_count += 1

            alert_message = (
                "URGENT: Product is out of stock"
            )

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            high_count += 1

            alert_message = (
                "Restock high-risk product soon"
            )

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            medium_count += 1

            alert_message = (
                "Monitor medium-risk product"
            )

        else:

            risk_level = "Low"
            risk_score = 0
            low_count += 1

            alert_message = (
                "Stock level is healthy"
            )

        total_risk_score += risk_score

        # --------------------------------------
        # PRODUCT RISK DATA
        # --------------------------------------

        risk_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "inventory_value": inventory_value,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

        # --------------------------------------
        # ALERTS
        # --------------------------------------

        if risk_level != "Low":

            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "stock": product.stock,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "alert": alert_message
            })

    # ------------------------------------------
    # AVERAGE RISK SCORE
    # ------------------------------------------

    average_risk_score = round(
        total_risk_score /
        len(products),
        2
    )

    # ------------------------------------------
    # OVERALL RISK
    # ------------------------------------------

    if average_risk_score >= 75:

        overall_risk = "Critical"

    elif average_risk_score >= 50:

        overall_risk = "High"

    elif average_risk_score > 0:

        overall_risk = "Medium"

    else:

        overall_risk = "Low"

    # ------------------------------------------
    # SORT PRODUCTS BY RISK
    # ------------------------------------------

    risk_products.sort(
        key=lambda x: (
            -x["risk_score"],
            x["stock"],
            -x["inventory_value"]
        )
    )

    # ------------------------------------------
    # HIGHEST / LOWEST RISK PRODUCT
    # ------------------------------------------

    highest_risk_product = risk_products[0]

    lowest_risk_product = sorted(
        risk_products,
        key=lambda x: (
            x["risk_score"],
            -x["stock"],
            x["inventory_value"]
        )
    )[0]

    # ------------------------------------------
    # SORT ALERTS
    # ------------------------------------------

    alerts.sort(
        key=lambda x: (
            -x["risk_score"],
            x["stock"]
        )
    )

    # ------------------------------------------
    # RECOMMENDATION
    # ------------------------------------------

    if critical_count > 0:

        recommendation = (
            "Immediate restocking required "
            "for critical products"
        )

    elif high_count > 0:

        recommendation = (
            "Restock high-risk products soon"
        )

    elif medium_count > 0:

        recommendation = (
            "Monitor medium-risk products"
        )

    else:

        recommendation = (
            "Inventory levels are healthy"
        )

    # ------------------------------------------
    # FINAL RESPONSE
    # ------------------------------------------

    return {

        "total_products":
            len(products),

        "total_stock":
            total_stock,

        "total_inventory_value":
            total_inventory_value,

        "risk_summary": {

            "critical":
                critical_count,

            "high":
                high_count,

            "medium":
                medium_count,

            "low":
                low_count
        },

        "average_risk_score":
            average_risk_score,

        "overall_risk":
            overall_risk,

        "highest_risk_product":
            highest_risk_product,

        "lowest_risk_product":
            lowest_risk_product,

        "alerts":
            alerts,

        "recommendation":
            recommendation
    } 
    # ==================================================
# STEP 6.39 — INVENTORY DASHBOARD DISTRIBUTION
# ==================================================

@app.get("/products/inventory-dashboard-distribution")
def get_inventory_dashboard_distribution(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    # ------------------------------------------
    # EMPTY DATABASE
    # ------------------------------------------

    if not products:

        return {
            "total_products": 0,
            "total_inventory_value": 0,

            "distribution": {
                "high_value": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },

                "medium_value": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },

                "low_value": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                }
            },

            "products": {
                "high_value": [],
                "medium_value": [],
                "low_value": []
            }
        }

    # ------------------------------------------
    # TOTAL INVENTORY VALUE
    # ------------------------------------------

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    # ------------------------------------------
    # INITIAL DISTRIBUTION
    # ------------------------------------------

    distribution = {

        "high_value": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        },

        "medium_value": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        },

        "low_value": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    high_value_products = []
    medium_value_products = []
    low_value_products = []

    # ------------------------------------------
    # CLASSIFY PRODUCTS
    # ------------------------------------------

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        # --------------------------------------
        # VALUE CLASSIFICATION
        # --------------------------------------

        if stock_value > 500000:

            category = "high_value"

            high_value_products.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value
            })

        elif stock_value >= 100000:

            category = "medium_value"

            medium_value_products.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value
            })

        else:

            category = "low_value"

            low_value_products.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value
            })

        # --------------------------------------
        # UPDATE DISTRIBUTION
        # --------------------------------------

        distribution[category]["product_count"] += 1

        distribution[category]["total_stock"] += (
            product.stock
        )

        distribution[category]["inventory_value"] += (
            stock_value
        )

    # ------------------------------------------
    # CALCULATE PERCENTAGES
    # ------------------------------------------

    for category in distribution:

        product_count = (
            distribution[category]["product_count"]
        )

        if len(products) > 0:

            distribution[category]["percentage"] = round(
                (
                    product_count /
                    len(products)
                ) * 100,
                2
            )

        else:

            distribution[category]["percentage"] = 0

    # ------------------------------------------
    # SORT PRODUCTS
    # ------------------------------------------

    high_value_products.sort(
        key=lambda product:
        product["stock_value"],
        reverse=True
    )

    medium_value_products.sort(
        key=lambda product:
        product["stock_value"],
        reverse=True
    )

    low_value_products.sort(
        key=lambda product:
        product["stock_value"],
        reverse=True
    )

    # ------------------------------------------
    # FINAL RESPONSE
    # ------------------------------------------

    return {

        "total_products":
            len(products),

        "total_inventory_value":
            total_inventory_value,

        "distribution":
            distribution,

        "products": {

            "high_value":
                high_value_products,

            "medium_value":
                medium_value_products,

            "low_value":
                low_value_products
        }
    }

    # ==================================================
# STEP 6.40 — INVENTORY DASHBOARD SUMMARY
# ==================================================

@app.get("/products/inventory-dashboard-summary")
def get_inventory_dashboard_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    # -----------------------------------------------
    # EMPTY DATABASE
    # -----------------------------------------------

    if not products:
        return {
            "dashboard": {
                "total_products": 0,
                "total_stock": 0,
                "total_inventory_value": 0
            },

            "health": {
                "health_score": 0,
                "status": "No Data"
            },

            "risk": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "average_risk_score": 0,
                "overall_risk": "No Data"
            },

            "value_distribution": {
                "high_value": {
                    "product_count": 0,
                    "inventory_value": 0
                },
                "medium_value": {
                    "product_count": 0,
                    "inventory_value": 0
                },
                "low_value": {
                    "product_count": 0,
                    "inventory_value": 0
                }
            },

            "highest_value_product": None,
            "highest_risk_product": None,

            "recommendations": []
        }

    # -----------------------------------------------
    # BASIC DASHBOARD DATA
    # -----------------------------------------------

    total_products = len(products)

    total_stock = sum(
        product.stock
        for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    # -----------------------------------------------
    # RISK CALCULATION
    # -----------------------------------------------

    critical = 0
    high = 0
    medium = 0
    low = 0

    total_risk_score = 0

    risk_products = []

    for product in products:

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            critical += 1

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            high += 1

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            medium += 1

        else:

            risk_level = "Low"
            risk_score = 0
            low += 1

        total_risk_score += risk_score

        risk_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    average_risk_score = round(
        total_risk_score / total_products,
        2
    )

    if average_risk_score >= 75:

        overall_risk = "Critical"

    elif average_risk_score >= 50:

        overall_risk = "High"

    elif average_risk_score > 0:

        overall_risk = "Medium"

    else:

        overall_risk = "Low"

    # -----------------------------------------------
    # INVENTORY HEALTH
    # -----------------------------------------------

    healthy_products = sum(
        1
        for product in products
        if product.stock > 5
    )

    health_score = round(
        (
            healthy_products /
            total_products
        ) * 100,
        2
    )

    if health_score >= 80:

        health_status = "Excellent"

    elif health_score >= 60:

        health_status = "Good"

    elif health_score >= 40:

        health_status = "Moderate"

    else:

        health_status = "Poor"

    # -----------------------------------------------
    # VALUE DISTRIBUTION
    # -----------------------------------------------

    high_value = {
        "product_count": 0,
        "inventory_value": 0
    }

    medium_value = {
        "product_count": 0,
        "inventory_value": 0
    }

    low_value = {
        "product_count": 0,
        "inventory_value": 0
    }

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        if stock_value > 500000:

            high_value["product_count"] += 1
            high_value["inventory_value"] += stock_value

        elif stock_value >= 100000:

            medium_value["product_count"] += 1
            medium_value["inventory_value"] += stock_value

        else:

            low_value["product_count"] += 1
            low_value["inventory_value"] += stock_value

    # -----------------------------------------------
    # HIGHEST VALUE PRODUCT
    # -----------------------------------------------

    highest_value_product = max(
        products,
        key=lambda product:
        product.price * product.stock
    )

    highest_value_data = {
        "product_id": highest_value_product.id,
        "product_name": highest_value_product.name,
        "price": highest_value_product.price,
        "stock": highest_value_product.stock,
        "stock_value":
            highest_value_product.price *
            highest_value_product.stock
    }

    # -----------------------------------------------
    # HIGHEST RISK PRODUCT
    # -----------------------------------------------

    highest_risk_data = max(
        risk_products,
        key=lambda product:
        product["risk_score"]
    )

    # -----------------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------------

    recommendations = []

    for product in products:

        if product.stock == 0:

            recommendation = "Restock immediately"

        elif product.stock <= 5:

            recommendation = "Urgent restocking required"

        elif product.stock <= 10:

            recommendation = "Monitor stock level"

        else:

            recommendation = "Stock level healthy"

        recommendations.append({
            "product_id": product.id,
            "product_name": product.name,
            "stock": product.stock,
            "recommendation": recommendation
        })

    # -----------------------------------------------
    # FINAL RESPONSE
    # -----------------------------------------------

    return {

        "dashboard": {

            "total_products":
                total_products,

            "total_stock":
                total_stock,

            "total_inventory_value":
                total_inventory_value
        },

        "health": {

            "health_score":
                health_score,

            "status":
                health_status
        },

        "risk": {

            "critical":
                critical,

            "high":
                high,

            "medium":
                medium,

            "low":
                low,

            "average_risk_score":
                average_risk_score,

            "overall_risk":
                overall_risk
        },

        "value_distribution": {

            "high_value":
                high_value,

            "medium_value":
                medium_value,

            "low_value":
                low_value
        },

        "highest_value_product":
            highest_value_data,

        "highest_risk_product":
            highest_risk_data,

        "recommendations":
            recommendations
    } 
    # ==================================================
# STEP 6.41 — INVENTORY DASHBOARD ALERTS
# ==================================================

@app.get("/products/inventory-dashboard-alerts")
def get_inventory_dashboard_alerts(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    alerts = []

    critical_alerts = 0
    high_alerts = 0
    medium_alerts = 0

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        # ------------------------------------------
        # CRITICAL
        # ------------------------------------------

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            alert_type = "Critical Stock Alert"
            message = "Product is out of stock"
            action = "Restock immediately"

            critical_alerts += 1

            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "alert_type": alert_type,
                "message": message,
                "action": action
            })

        # ------------------------------------------
        # HIGH
        # ------------------------------------------

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            alert_type = "High Stock Risk"
            message = "Product stock is critically low"
            action = "Urgent restocking required"

            high_alerts += 1

            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "alert_type": alert_type,
                "message": message,
                "action": action
            })

        # ------------------------------------------
        # MEDIUM
        # ------------------------------------------

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            alert_type = "Medium Stock Alert"
            message = "Product stock needs monitoring"
            action = "Monitor and review stock"

            medium_alerts += 1

            alerts.append({
                "product_id": product.id,
                "product_name": product.name,
                "price": product.price,
                "stock": product.stock,
                "stock_value": stock_value,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "alert_type": alert_type,
                "message": message,
                "action": action
            })

    # ----------------------------------------------
    # SORT ALERTS BY RISK
    # ----------------------------------------------

    alerts.sort(
        key=lambda alert:
        alert["risk_score"],
        reverse=True
    )

    # ----------------------------------------------
    # OVERALL STATUS
    # ----------------------------------------------

    if critical_alerts > 0:

        overall_status = "Critical"

    elif high_alerts > 0:

        overall_status = "High"

    elif medium_alerts > 0:

        overall_status = "Medium"

    else:

        overall_status = "Healthy"

    # ----------------------------------------------
    # FINAL RESPONSE
    # ----------------------------------------------

    return {

        "total_products":
            len(products),

        "total_alerts":
            len(alerts),

        "critical_alerts":
            critical_alerts,

        "high_alerts":
            high_alerts,

        "medium_alerts":
            medium_alerts,

        "overall_status":
            overall_status,

        "alerts":
            alerts
    }
    # ==================================================
# STEP 6.42 — INVENTORY DASHBOARD RECOMMENDATIONS
# ==================================================

@app.get("/products/inventory-dashboard-recommendations")
def get_inventory_dashboard_recommendations(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    recommendations = []

    critical_count = 0
    high_count = 0
    medium_count = 0
    healthy_count = 0

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        # ------------------------------------------
        # CRITICAL
        # ------------------------------------------

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            priority = "Immediate"
            recommendation = "Restock immediately"

            critical_count += 1

        # ------------------------------------------
        # HIGH
        # ------------------------------------------

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            priority = "High"
            recommendation = "Urgent restocking required"

            high_count += 1

        # ------------------------------------------
        # MEDIUM
        # ------------------------------------------

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            priority = "Medium"
            recommendation = "Monitor stock and plan restocking"

            medium_count += 1

        # ------------------------------------------
        # HEALTHY
        # ------------------------------------------

        else:

            risk_level = "Low"
            risk_score = 0
            priority = "Low"
            recommendation = "Stock level healthy"

            healthy_count += 1

        recommendations.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "priority": priority,
            "recommendation": recommendation
        })

    # ----------------------------------------------
    # SORT BY RISK SCORE
    # ----------------------------------------------

    recommendations.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    # ----------------------------------------------
    # OVERALL PRIORITY
    # ----------------------------------------------

    if critical_count > 0:

        overall_priority = "Immediate"

    elif high_count > 0:

        overall_priority = "High"

    elif medium_count > 0:

        overall_priority = "Medium"

    else:

        overall_priority = "Low"

    # ----------------------------------------------
    # FINAL RESPONSE
    # ----------------------------------------------

    return {

        "total_products":
            len(products),

        "summary": {

            "critical":
                critical_count,

            "high":
                high_count,

            "medium":
                medium_count,

            "healthy":
                healthy_count
        },

        "overall_priority":
            overall_priority,

        "recommendations":
            recommendations
    }
    # ==================================================
# STEP 6.43 — INVENTORY DASHBOARD ACTION PLAN
# ==================================================

@app.get("/products/inventory-dashboard-action-plan")
def get_inventory_dashboard_action_plan(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    action_plan = []

    critical_count = 0
    high_count = 0
    medium_count = 0
    healthy_count = 0

    for product in products:

        stock_value = (
            product.price *
            product.stock
        )

        # ------------------------------------------
        # CRITICAL
        # ------------------------------------------

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            priority = "Immediate"
            action = "Restock immediately"
            reason = "Product is out of stock"

            critical_count += 1

        # ------------------------------------------
        # HIGH
        # ------------------------------------------

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            priority = "High"
            action = "Urgent restocking required"
            reason = "Product stock is critically low"

            high_count += 1

        # ------------------------------------------
        # MEDIUM
        # ------------------------------------------

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            priority = "Medium"
            action = "Monitor and plan restocking"
            reason = "Product stock needs monitoring"

            medium_count += 1

        # ------------------------------------------
        # HEALTHY
        # ------------------------------------------

        else:

            risk_level = "Low"
            risk_score = 0
            priority = "Low"
            action = "No immediate action"
            reason = "Stock level is healthy"

            healthy_count += 1

        action_plan.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "priority": priority,
            "action": action,
            "reason": reason
        })

    # ----------------------------------------------
    # SORT BY RISK
    # ----------------------------------------------

    action_plan.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    # ----------------------------------------------
    # OVERALL PRIORITY
    # ----------------------------------------------

    if critical_count > 0:

        overall_priority = "Immediate"

    elif high_count > 0:

        overall_priority = "High"

    elif medium_count > 0:

        overall_priority = "Medium"

    else:

        overall_priority = "Low"

    # ----------------------------------------------
    # FINAL RESPONSE
    # ----------------------------------------------

    return {

        "total_products":
            len(products),

        "summary": {

            "critical":
                critical_count,

            "high":
                high_count,

            "medium":
                medium_count,

            "healthy":
                healthy_count
        },

        "overall_priority":
            overall_priority,

        "action_plan":
            action_plan
    }
    # ==================================================
# STEP 6.44 — INVENTORY DASHBOARD HEALTH REPORT
# ==================================================

@app.get("/products/inventory-dashboard-health-report")
def get_inventory_dashboard_health_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    # ----------------------------------------------
    # EMPTY DATABASE
    # ----------------------------------------------

    if not products:
        return {
            "health_report": {
                "total_products": 0,
                "total_stock": 0,
                "total_inventory_value": 0,
                "health_score": 0,
                "health_status": "No Data"
            },

            "stock_status": {
                "healthy_products": 0,
                "low_stock_products": 0,
                "out_of_stock_products": 0
            },

            "risk_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },

            "recommendation": "Add products to generate inventory health report"
        }

    # ----------------------------------------------
    # BASIC METRICS
    # ----------------------------------------------

    total_products = len(products)

    total_stock = sum(
        product.stock
        for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    # ----------------------------------------------
    # STOCK STATUS
    # ----------------------------------------------

    healthy_products = 0
    low_stock_products = 0
    out_of_stock_products = 0

    # ----------------------------------------------
    # RISK SUMMARY
    # ----------------------------------------------

    critical = 0
    high = 0
    medium = 0
    low = 0

    total_risk_score = 0

    for product in products:

        # ------------------------------------------
        # STOCK STATUS
        # ------------------------------------------

        if product.stock == 0:

            out_of_stock_products += 1

        elif product.stock <= 5:

            low_stock_products += 1

        else:

            healthy_products += 1

        # ------------------------------------------
        # RISK LEVEL
        # ------------------------------------------

        if product.stock == 0:

            critical += 1
            risk_score = 100

        elif product.stock <= 5:

            high += 1
            risk_score = 75

        elif product.stock <= 10:

            medium += 1
            risk_score = 50

        else:

            low += 1
            risk_score = 0

        total_risk_score += risk_score

    # ----------------------------------------------
    # HEALTH SCORE
    # ----------------------------------------------

    health_score = round(
        (
            healthy_products /
            total_products
        ) * 100,
        2
    )

    # ----------------------------------------------
    # HEALTH STATUS
    # ----------------------------------------------

    if health_score >= 80:

        health_status = "Excellent"

    elif health_score >= 60:

        health_status = "Good"

    elif health_score >= 40:

        health_status = "Moderate"

    else:

        health_status = "Poor"

    # ----------------------------------------------
    # RECOMMENDATION
    # ----------------------------------------------

    if out_of_stock_products > 0:

        recommendation = "Immediate restocking required"

    elif low_stock_products > 0:

        recommendation = "Review low-stock products and plan restocking"

    elif medium > 0:

        recommendation = "Monitor medium-risk inventory"

    else:

        recommendation = "Inventory health is good"

    # ----------------------------------------------
    # FINAL RESPONSE
    # ----------------------------------------------

    return {

        "health_report": {

            "total_products":
                total_products,

            "total_stock":
                total_stock,

            "total_inventory_value":
                total_inventory_value,

            "health_score":
                health_score,

            "health_status":
                health_status
        },

        "stock_status": {

            "healthy_products":
                healthy_products,

            "low_stock_products":
                low_stock_products,

            "out_of_stock_products":
                out_of_stock_products
        },

        "risk_summary": {

            "critical":
                critical,

            "high":
                high,

            "medium":
                medium,

            "low":
                low
        },

        "recommendation":
            recommendation
    }
     # ==================================================
# STEP 6.45 — INVENTORY DASHBOARD RISK REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-report")
def get_inventory_dashboard_risk_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    # ----------------------------------------------
    # EMPTY DATABASE
    # ----------------------------------------------

    if not products:
        return {
            "risk_report": {
                "total_products": 0,
                "total_inventory_value": 0,
                "average_risk_score": 0,
                "overall_risk": "No Data"
            },

            "risk_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },

            "highest_risk_product": None,

            "recommendation":
                "Add products to generate risk report"
        }

    # ----------------------------------------------
    # BASIC DATA
    # ----------------------------------------------

    total_products = len(products)

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    critical = 0
    high = 0
    medium = 0
    low = 0

    total_risk_score = 0

    risk_products = []

    # ----------------------------------------------
    # RISK CALCULATION
    # ----------------------------------------------

    for product in products:

        if product.stock == 0:

            risk_level = "Critical"
            risk_score = 100
            critical += 1

        elif product.stock <= 5:

            risk_level = "High"
            risk_score = 75
            high += 1

        elif product.stock <= 10:

            risk_level = "Medium"
            risk_score = 50
            medium += 1

        else:

            risk_level = "Low"
            risk_score = 0
            low += 1

        total_risk_score += risk_score

        risk_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value":
                product.price * product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    # ----------------------------------------------
    # AVERAGE RISK
    # ----------------------------------------------

    average_risk_score = round(
        total_risk_score /
        total_products,
        2
    )

    # ----------------------------------------------
    # OVERALL RISK
    # ----------------------------------------------

    if average_risk_score >= 75:

        overall_risk = "Critical"

    elif average_risk_score >= 50:

        overall_risk = "High"

    elif average_risk_score > 0:

        overall_risk = "Medium"

    else:

        overall_risk = "Low"

    # ----------------------------------------------
    # SORT BY RISK
    # ----------------------------------------------

    risk_products.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    # ----------------------------------------------
    # HIGHEST RISK PRODUCT
    # ----------------------------------------------

    highest_risk_product = risk_products[0]

    # ----------------------------------------------
    # RECOMMENDATION
    # ----------------------------------------------

    if critical > 0:

        recommendation = (
            "Immediate restocking required "
            "for critical products"
        )

    elif high > 0:

        recommendation = (
            "Urgent restocking required "
            "for high-risk products"
        )

    elif medium > 0:

        recommendation = (
            "Monitor medium-risk products "
            "and plan restocking"
        )

    else:

        recommendation = (
            "Inventory risk is currently low"
        )

    # ----------------------------------------------
    # FINAL RESPONSE
    # ----------------------------------------------

    return {

        "risk_report": {

            "total_products":
                total_products,

            "total_inventory_value":
                total_inventory_value,

            "average_risk_score":
                average_risk_score,

            "overall_risk":
                overall_risk
        },

        "risk_summary": {

            "critical":
                critical,

            "high":
                high,

            "medium":
                medium,

            "low":
                low
        },

        "highest_risk_product":
            highest_risk_product,

        "products":
            risk_products,

        "recommendation":
            recommendation
    }
    # ==================================================
# STEP 6.46 — INVENTORY DASHBOARD RISK RECOMMENDATIONS
# ==================================================

@app.get("/products/inventory-dashboard-risk-recommendations")
def get_inventory_dashboard_risk_recommendations(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "overall_priority": "No Data",
            "recommendations": []
        }

    critical = 0
    high = 0
    medium = 0
    low = 0

    recommendations = []

    for product in products:

        if product.stock == 0:
            risk_level = "Critical"
            risk_score = 100
            priority = "Critical"
            recommendation = (
                "Immediate restocking required"
            )
            critical += 1

        elif product.stock <= 5:
            risk_level = "High"
            risk_score = 75
            priority = "High"
            recommendation = (
                "Urgent restocking required"
            )
            high += 1

        elif product.stock <= 10:
            risk_level = "Medium"
            risk_score = 50
            priority = "Medium"
            recommendation = (
                "Monitor stock and plan restocking"
            )
            medium += 1

        else:
            risk_level = "Low"
            risk_score = 0
            priority = "Low"
            recommendation = (
                "Stock level healthy"
            )
            low += 1

        recommendations.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": product.price * product.stock,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "priority": priority,
            "recommendation": recommendation
        })

    if critical > 0:
        overall_priority = "Critical"
    elif high > 0:
        overall_priority = "High"
    elif medium > 0:
        overall_priority = "Medium"
    else:
        overall_priority = "Low"

    recommendations.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    return {
        "total_products": len(products),
        "summary": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },
        "overall_priority": overall_priority,
        "recommendations": recommendations
    }
    # ==================================================
# STEP 6.47 — INVENTORY DASHBOARD RISK ACTION PLAN
# ==================================================

@app.get("/products/inventory-dashboard-risk-action-plan")
def get_inventory_dashboard_risk_action_plan(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "total_products": 0,
            "summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "overall_priority": "No Data",
            "action_plan": []
        }

    critical = 0
    high = 0
    medium = 0
    low = 0

    action_plan = []

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"
            risk_score = 100
            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Product is completely out of stock"
            critical += 1

        elif product.stock <= 5:
            risk_level = "High"
            risk_score = 75
            priority = "High"
            action = "Urgent Restocking"
            reason = "Product stock is critically low"
            high += 1

        elif product.stock <= 10:
            risk_level = "Medium"
            risk_score = 50
            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"
            medium += 1

        else:
            risk_level = "Low"
            risk_score = 0
            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"
            low += 1

        action_plan.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "priority": priority,
            "action": action,
            "reason": reason
        })

    if critical > 0:
        overall_priority = "Critical"
    elif high > 0:
        overall_priority = "High"
    elif medium > 0:
        overall_priority = "Medium"
    else:
        overall_priority = "Low"

    action_plan.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    return {
        "total_products": len(products),
        "summary": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },
        "overall_priority": overall_priority,
        "action_plan": action_plan
    }
    # ==================================================
# STEP 6.48 — INVENTORY DASHBOARD RISK HEALTH REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-health-report")
def get_inventory_dashboard_risk_health_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "risk_health_report": {
                "total_products": 0,
                "total_stock": 0,
                "total_inventory_value": 0,
                "average_risk_score": 0,
                "risk_health_score": 0,
                "health_status": "No Data",
                "overall_risk": "No Data"
            },
            "risk_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "recommendation": "Add products to generate risk health report"
        }

    total_products = len(products)

    total_stock = sum(
        product.stock
        for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    critical = 0
    high = 0
    medium = 0
    low = 0

    total_risk_score = 0

    for product in products:

        if product.stock == 0:
            risk_score = 100
            critical += 1

        elif product.stock <= 5:
            risk_score = 75
            high += 1

        elif product.stock <= 10:
            risk_score = 50
            medium += 1

        else:
            risk_score = 0
            low += 1

        total_risk_score += risk_score

    average_risk_score = round(
        total_risk_score / total_products,
        2
    )

    # Risk status
    if average_risk_score >= 75:
        overall_risk = "Critical"
    elif average_risk_score >= 50:
        overall_risk = "High"
    elif average_risk_score > 0:
        overall_risk = "Medium"
    else:
        overall_risk = "Low"

    # Risk health score
    risk_health_score = round(
        100 - average_risk_score,
        2
    )

    if risk_health_score >= 90:
        health_status = "Excellent"
    elif risk_health_score >= 75:
        health_status = "Good"
    elif risk_health_score >= 50:
        health_status = "Moderate"
    else:
        health_status = "Poor"

    if critical > 0:
        recommendation = (
            "Immediate action required for "
            "critical-risk products"
        )
    elif high > 0:
        recommendation = (
            "Urgent restocking required for "
            "high-risk products"
        )
    elif medium > 0:
        recommendation = (
            "Monitor medium-risk products "
            "and plan restocking"
        )
    else:
        recommendation = (
            "Inventory risk is healthy"
        )

    return {
        "risk_health_report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "average_risk_score": average_risk_score,
            "risk_health_score": risk_health_score,
            "health_status": health_status,
            "overall_risk": overall_risk
        },
        "risk_summary": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },
        "recommendation": recommendation
    }
    # ==================================================
# STEP 6.49 — INVENTORY DASHBOARD RISK DISTRIBUTION REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-distribution-report")
def get_inventory_dashboard_risk_distribution_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "risk_distribution_report": {
                "total_products": 0,
                "total_stock": 0,
                "total_inventory_value": 0
            },
            "distribution": {
                "critical": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },
                "high": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },
                "medium": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },
                "low": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                }
            }
        }

    total_products = len(products)

    total_stock = sum(
        product.stock
        for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    distribution = {
        "critical": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "high": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "medium": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "low": {
            "product_count": 0,
            "percentage": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "critical"

        elif product.stock <= 5:
            risk_level = "high"

        elif product.stock <= 10:
            risk_level = "medium"

        else:
            risk_level = "low"

        distribution[risk_level]["product_count"] += 1

        distribution[risk_level]["total_stock"] += product.stock

        distribution[risk_level]["inventory_value"] += stock_value

    for risk_level in distribution:

        count = distribution[risk_level]["product_count"]

        distribution[risk_level]["percentage"] = round(
            (count / total_products) * 100,
            2
        )

    return {
        "risk_distribution_report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value
        },
        "distribution": distribution
    }
  # ==================================================
# STEP 6.50 — INVENTORY DASHBOARD RISK RANKING REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-report")
def get_inventory_dashboard_risk_ranking_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "risk_ranking_report": {
                "total_products": 0,
                "overall_risk": "No Data",
                "average_risk_score": 0
            },
            "ranking": []
        }

    total_products = len(products)

    total_risk_score = 0

    ranking = []

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"
            risk_score = 100

        elif product.stock <= 5:
            risk_level = "High"
            risk_score = 75

        elif product.stock <= 10:
            risk_level = "Medium"
            risk_score = 50

        else:
            risk_level = "Low"
            risk_score = 0

        total_risk_score += risk_score

        ranking.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    average_risk_score = round(
        total_risk_score / total_products,
        2
    )

    if average_risk_score >= 75:
        overall_risk = "Critical"

    elif average_risk_score >= 50:
        overall_risk = "High"

    elif average_risk_score > 0:
        overall_risk = "Medium"

    else:
        overall_risk = "Low"

    ranking.sort(
        key=lambda product:
        product["risk_score"],
        reverse=True
    )

    for index, product in enumerate(
        ranking,
        start=1
    ):
        product["rank"] = index

    return {
        "risk_ranking_report": {
            "total_products": total_products,
            "overall_risk": overall_risk,
            "average_risk_score": average_risk_score
        },
        "ranking": ranking
    }
    # ==================================================
# STEP 6.51 — INVENTORY DASHBOARD RISK RANKING SUMMARY
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-summary")
def get_inventory_dashboard_risk_ranking_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "risk_ranking_summary": {
                "total_products": 0,
                "total_inventory_value": 0,
                "overall_risk": "No Data",
                "average_risk_score": 0
            },
            "highest_risk_product": None,
            "top_ranked_product": None,
            "recommendation": "No inventory data available"
        }

    total_products = len(products)

    total_inventory_value = 0
    total_risk_score = 0

    ranking = []

    for product in products:

        stock_value = product.price * product.stock

        total_inventory_value += stock_value

        if product.stock == 0:
            risk_level = "Critical"
            risk_score = 100

        elif product.stock <= 5:
            risk_level = "High"
            risk_score = 75

        elif product.stock <= 10:
            risk_level = "Medium"
            risk_score = 50

        else:
            risk_level = "Low"
            risk_score = 0

        total_risk_score += risk_score

        ranking.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "risk_level": risk_level,
            "risk_score": risk_score
        })

    average_risk_score = round(
        total_risk_score / total_products,
        2
    )

    if average_risk_score >= 75:
        overall_risk = "Critical"

    elif average_risk_score >= 50:
        overall_risk = "High"

    elif average_risk_score > 0:
        overall_risk = "Medium"

    else:
        overall_risk = "Low"

    ranking.sort(
        key=lambda product: (
            product["risk_score"],
            product["stock_value"]
        ),
        reverse=True
    )

    for index, product in enumerate(
        ranking,
        start=1
    ):
        product["rank"] = index

    highest_risk_product = ranking[0]

    if overall_risk == "Critical":
        recommendation = "Immediate action required for critical-risk inventory"

    elif overall_risk == "High":
        recommendation = "Prioritize high-risk products and plan restocking"

    elif overall_risk == "Medium":
        recommendation = "Monitor medium-risk products and plan restocking"

    else:
        recommendation = "Inventory risk is low and stock levels are healthy"

    return {
        "risk_ranking_summary": {
            "total_products": total_products,
            "total_inventory_value": total_inventory_value,
            "overall_risk": overall_risk,
            "average_risk_score": average_risk_score
        },
        "highest_risk_product": {
            "product_id": highest_risk_product["product_id"],
            "product_name": highest_risk_product["product_name"],
            "risk_level": highest_risk_product["risk_level"],
            "risk_score": highest_risk_product["risk_score"]
        },
        "top_ranked_product": highest_risk_product,
        "recommendation": recommendation
    }   
    # ==================================================
# STEP 6.52 — INVENTORY DASHBOARD RISK RANKING DETAILS
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-details")
def get_inventory_dashboard_risk_ranking_details(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "risk_ranking_details": {
                "total_products": 0,
                "overall_risk": "No Data",
                "average_risk_score": 0
            },
            "ranking": []
        }

    total_products = len(products)
    total_risk_score = 0

    ranking = []

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"
            risk_score = 100
            priority = "Critical"
            action = "Immediate Restocking Required"
            reason = "Product is out of stock"

        elif product.stock <= 5:
            risk_level = "High"
            risk_score = 75
            priority = "High"
            action = "Prioritize Restocking"
            reason = "Product stock is critically low"

        elif product.stock <= 10:
            risk_level = "Medium"
            risk_score = 50
            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:
            risk_level = "Low"
            risk_score = 0
            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"

        total_risk_score += risk_score

        ranking.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "priority": priority,
            "action": action,
            "reason": reason
        })

    average_risk_score = round(
        total_risk_score / total_products,
        2
    )

    if average_risk_score >= 75:
        overall_risk = "Critical"

    elif average_risk_score >= 50:
        overall_risk = "High"

    elif average_risk_score > 0:
        overall_risk = "Medium"

    else:
        overall_risk = "Low"

    ranking.sort(
        key=lambda product: (
            product["risk_score"],
            product["stock_value"]
        ),
        reverse=True
    )

    for index, product in enumerate(
        ranking,
        start=1
    ):
        product["rank"] = index

    return {
        "risk_ranking_details": {
            "total_products": total_products,
            "overall_risk": overall_risk,
            "average_risk_score": average_risk_score
        },
        "ranking": ranking
    }
    # ==================================================
# STEP 6.53 — INVENTORY DASHBOARD RISK RANKING ACTION PLAN
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-action-plan")
def get_inventory_dashboard_risk_ranking_action_plan(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "action_plan_summary": {
                "total_products": 0,
                "overall_priority": "No Data",
                "average_risk_score": 0
            },
            "action_plan": []
        }

    total_products = len(products)
    total_risk_score = 0

    action_plan = []

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"
            risk_score = 100
            priority = "Critical"
            action = "Immediate Restocking Required"
            reason = "Product is out of stock"

        elif product.stock <= 5:
            risk_level = "High"
            risk_score = 75
            priority = "High"
            action = "Prioritize Restocking"
            reason = "Product stock is critically low"

        elif product.stock <= 10:
            risk_level = "Medium"
            risk_score = 50
            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:
            risk_level = "Low"
            risk_score = 0
            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"

        total_risk_score += risk_score

        action_plan.append({
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "stock": product.stock,
            "stock_value": stock_value,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "priority": priority,
            "action": action,
            "reason": reason
        })

    average_risk_score = round(
        total_risk_score / total_products,
        2
    )

    if average_risk_score >= 75:
        overall_priority = "Critical"

    elif average_risk_score >= 50:
        overall_priority = "High"

    elif average_risk_score > 0:
        overall_priority = "Medium"

    else:
        overall_priority = "Low"

    action_plan.sort(
        key=lambda product: (
            product["risk_score"],
            product["stock_value"]
        ),
        reverse=True
    )

    for index, product in enumerate(
        action_plan,
        start=1
    ):
        product["rank"] = index

    return {
        "action_plan_summary": {
            "total_products": total_products,
            "overall_priority": overall_priority,
            "average_risk_score": average_risk_score
        },
        "action_plan": action_plan
    }
    # ==================================================
# STEP 6.54 — INVENTORY DASHBOARD RISK RANKING HEALTH REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-health-report")
def get_inventory_dashboard_risk_ranking_health_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "health_report": {
                "total_products": 0,
                "total_stock": 0,
                "total_inventory_value": 0,
                "average_risk_score": 0,
                "health_score": 0,
                "health_status": "No Data",
                "overall_risk": "No Data"
            },
            "risk_summary": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "recommendation": "No inventory data available"
        }

    total_products = len(products)
    total_stock = 0
    total_inventory_value = 0
    total_risk_score = 0

    critical = 0
    high = 0
    medium = 0
    low = 0

    for product in products:

        total_stock += product.stock

        stock_value = product.price * product.stock
        total_inventory_value += stock_value

        if product.stock == 0:
            risk_level = "Critical"
            risk_score = 100
            critical += 1

        elif product.stock <= 5:
            risk_level = "High"
            risk_score = 75
            high += 1

        elif product.stock <= 10:
            risk_level = "Medium"
            risk_score = 50
            medium += 1

        else:
            risk_level = "Low"
            risk_score = 0
            low += 1

        total_risk_score += risk_score

    average_risk_score = round(
        total_risk_score / total_products,
        2
    )

    # Health score is inverse of average risk
    health_score = round(
        100 - average_risk_score,
        2
    )

    if health_score >= 80:
        health_status = "Excellent"

    elif health_score >= 60:
        health_status = "Good"

    elif health_score >= 40:
        health_status = "Needs Attention"

    else:
        health_status = "Critical"

    if average_risk_score >= 75:
        overall_risk = "Critical"

    elif average_risk_score >= 50:
        overall_risk = "High"

    elif average_risk_score > 0:
        overall_risk = "Medium"

    else:
        overall_risk = "Low"

    if overall_risk == "Critical":
        recommendation = (
            "Immediate action required for critical-risk inventory"
        )

    elif overall_risk == "High":
        recommendation = (
            "Prioritize high-risk products and plan urgent restocking"
        )

    elif overall_risk == "Medium":
        recommendation = (
            "Monitor medium-risk products and plan restocking"
        )

    else:
        recommendation = (
            "Inventory risk is low and stock levels are healthy"
        )

    return {
        "health_report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "average_risk_score": average_risk_score,
            "health_score": health_score,
            "health_status": health_status,
            "overall_risk": overall_risk
        },
        "risk_summary": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        },
        "recommendation": recommendation
    }
    # ==================================================
# STEP 6.55 — INVENTORY DASHBOARD RISK RANKING DISTRIBUTION REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-report")
def get_inventory_dashboard_risk_ranking_distribution_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    if not products:
        return {
            "distribution_report": {
                "total_products": 0,
                "total_stock": 0,
                "total_inventory_value": 0
            },
            "distribution": {
                "critical": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },
                "high": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },
                "medium": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                },
                "low": {
                    "product_count": 0,
                    "percentage": 0,
                    "total_stock": 0,
                    "inventory_value": 0
                }
            }
        }

    total_products = len(products)
    total_stock = 0
    total_inventory_value = 0

    risk_data = {
        "critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "high": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        total_stock += product.stock
        total_inventory_value += stock_value

        if product.stock == 0:
            risk_category = "critical"

        elif product.stock <= 5:
            risk_category = "high"

        elif product.stock <= 10:
            risk_category = "medium"

        else:
            risk_category = "low"

        risk_data[risk_category]["product_count"] += 1
        risk_data[risk_category]["total_stock"] += product.stock
        risk_data[risk_category]["inventory_value"] += stock_value

    distribution = {}

    for category, data in risk_data.items():

        percentage = round(
            (data["product_count"] / total_products) * 100,
            2
        )

        distribution[category] = {
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"]
        }

    return {
        "distribution_report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value
        },
        "distribution": distribution
    }
    # ==================================================
# STEP 6.56 — INVENTORY DASHBOARD RISK RANKING DISTRIBUTION SUMMARY
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-summary")
def get_inventory_dashboard_risk_ranking_distribution_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)
    total_stock = sum(product.stock for product in products)
    total_inventory_value = sum(
        product.price * product.stock for product in products
    )

    critical = 0
    high = 0
    medium = 0
    low = 0

    for product in products:

        if product.stock == 0:
            critical += 1

        elif product.stock <= 5:
            high += 1

        elif product.stock <= 10:
            medium += 1

        else:
            low += 1

    if total_products > 0:
        critical_percentage = round(
            (critical / total_products) * 100, 2
        )
        high_percentage = round(
            (high / total_products) * 100, 2
        )
        medium_percentage = round(
            (medium / total_products) * 100, 2
        )
        low_percentage = round(
            (low / total_products) * 100, 2
        )
    else:
        critical_percentage = 0
        high_percentage = 0
        medium_percentage = 0
        low_percentage = 0

    average_risk_score = 0

    if total_products > 0:

        total_risk_score = 0

        for product in products:

            if product.stock == 0:
                risk_score = 100

            elif product.stock <= 5:
                risk_score = 75

            elif product.stock <= 10:
                risk_score = 50

            else:
                risk_score = 0

            total_risk_score += risk_score

        average_risk_score = round(
            total_risk_score / total_products,
            2
        )

    if average_risk_score >= 75:
        overall_risk = "Critical"

    elif average_risk_score >= 50:
        overall_risk = "High"

    elif average_risk_score > 0:
        overall_risk = "Medium"

    else:
        overall_risk = "Low"

    return {
        "distribution_summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "average_risk_score": average_risk_score,
            "overall_risk": overall_risk
        },
        "risk_distribution": {
            "critical": {
                "product_count": critical,
                "percentage": critical_percentage
            },
            "high": {
                "product_count": high,
                "percentage": high_percentage
            },
            "medium": {
                "product_count": medium,
                "percentage": medium_percentage
            },
            "low": {
                "product_count": low,
                "percentage": low_percentage
            }
        }
    }
    # ==================================================
# STEP 6.57 — INVENTORY DASHBOARD RISK RANKING DISTRIBUTION DETAILS
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-details")
def get_inventory_dashboard_risk_ranking_distribution_details(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_categories = {
        "critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "high": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "critical"

        elif product.stock <= 5:
            risk_level = "high"

        elif product.stock <= 10:
            risk_level = "medium"

        else:
            risk_level = "low"

        risk_categories[risk_level]["product_count"] += 1
        risk_categories[risk_level]["total_stock"] += product.stock
        risk_categories[risk_level]["inventory_value"] += stock_value

    details = []

    for risk_level in ["critical", "high", "medium", "low"]:

        data = risk_categories[risk_level]

        if total_products > 0:
            percentage = round(
                (data["product_count"] / total_products) * 100,
                2
            )
        else:
            percentage = 0

        details.append({
            "risk_level": risk_level.capitalize(),
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"]
        })

    return {
        "distribution_details": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value
        },
        "risk_distribution": details
    }
    # ==================================================
# STEP 6.58 — INVENTORY DASHBOARD RISK RANKING DISTRIBUTION ACTION PLAN
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan")
def get_inventory_dashboard_risk_ranking_distribution_action_plan(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_categories = {
        "critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "high": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "critical"

        elif product.stock <= 5:
            risk_level = "high"

        elif product.stock <= 10:
            risk_level = "medium"

        else:
            risk_level = "low"

        risk_categories[risk_level]["product_count"] += 1
        risk_categories[risk_level]["total_stock"] += product.stock
        risk_categories[risk_level]["inventory_value"] += stock_value

    action_plan = []

    for risk_level in ["critical", "high", "medium", "low"]:

        data = risk_categories[risk_level]

        if total_products > 0:
            percentage = round(
                (data["product_count"] / total_products) * 100,
                2
            )
        else:
            percentage = 0

        if risk_level == "critical":

            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "high":

            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "medium":

            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:

            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"

        action_plan.append({
            "risk_level": risk_level.capitalize(),
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": priority,
            "action": action,
            "reason": reason
        })

    return {
        "action_plan_summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value
        },
        "risk_distribution_action_plan": action_plan
    }
    # ==================================================
# STEP 6.59 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN SUMMARY
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-summary")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    risk_stock = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    risk_inventory_value = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_counts[risk_level] += 1
        risk_stock[risk_level] += product.stock
        risk_inventory_value[risk_level] += stock_value

    if risk_counts["Critical"] > 0:
        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels require immediate action"

    elif risk_counts["High"] > 0:
        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk products require urgent restocking"

    elif risk_counts["Medium"] > 0:
        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:
        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All products have healthy stock levels"

    action_plan_summary = []

    for risk_level in ["Critical", "High", "Medium", "Low"]:

        if total_products > 0:
            percentage = round(
                (risk_counts[risk_level] / total_products) * 100,
                2
            )
        else:
            percentage = 0

        if risk_level == "Critical":
            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "High":
            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "Medium":
            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:
            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"

        action_plan_summary.append({
            "risk_level": risk_level,
            "product_count": risk_counts[risk_level],
            "percentage": percentage,
            "total_stock": risk_stock[risk_level],
            "inventory_value": risk_inventory_value[risk_level],
            "priority": priority,
            "action": action,
            "reason": reason
        })

    return {
        "summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "risk_distribution_action_plan_summary": action_plan_summary
    }
    # ==================================================
# STEP 6.60 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN DETAILS
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-details")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_details(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    detailed_action_plan = []

    for risk_level in ["Critical", "High", "Medium", "Low"]:

        data = risk_data[risk_level]

        if total_products > 0:
            percentage = round(
                (data["product_count"] / total_products) * 100,
                2
            )
        else:
            percentage = 0

        if risk_level == "Critical":

            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"
            recommended_step = "Restock immediately and review supplier availability"

        elif risk_level == "High":

            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"
            recommended_step = "Place urgent purchase orders and increase stock"

        elif risk_level == "Medium":

            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"
            recommended_step = "Monitor sales and plan the next restocking cycle"

        else:

            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"
            recommended_step = "Continue normal inventory monitoring"

        detailed_action_plan.append({
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": priority,
            "action": action,
            "reason": reason,
            "recommended_step": recommended_step
        })

    return {
        "action_plan_details": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value
        },
        "risk_distribution_action_plan_details": detailed_action_plan
    }
    # ==================================================
# STEP 6.61 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-report")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if risk_data["Critical"]["product_count"] > 0:

        overall_risk = "Critical"
        overall_priority = "Critical"
        overall_action = "Immediate Restocking"

    elif risk_data["High"]["product_count"] > 0:

        overall_risk = "High"
        overall_priority = "High"
        overall_action = "Urgent Restocking"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_risk = "Medium"
        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"

    else:

        overall_risk = "Low"
        overall_priority = "Low"
        overall_action = "No Immediate Action"

    risk_distribution = []

    for risk_level in ["Critical", "High", "Medium", "Low"]:

        data = risk_data[risk_level]

        if total_products > 0:
            percentage = round(
                (data["product_count"] / total_products) * 100,
                2
            )
        else:
            percentage = 0

        if risk_level == "Critical":

            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "High":

            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "Medium":

            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:

            action = "No Immediate Action"
            reason = "Stock level is healthy"

        risk_distribution.append({
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": risk_level,
            "action": action,
            "reason": reason
        })

    return {
        "report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_risk": overall_risk,
            "overall_priority": overall_priority,
            "overall_action": overall_action
        },
        "risk_distribution": risk_distribution
    }
    # ==================================================
# STEP 6.62 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    ranking_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    ranking = []

    for risk_level in ["Critical", "High", "Medium", "Low"]:

        data = risk_data[risk_level]

        if total_products > 0:
            percentage = round(
                (data["product_count"] / total_products) * 100,
                2
            )
        else:
            percentage = 0

        if risk_level == "Critical":

            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "High":

            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "Medium":

            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:

            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"

        ranking.append({
            "rank": ranking_order[risk_level],
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": priority,
            "action": action,
            "reason": reason
        })

    return {
        "ranking_summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value
        },
        "action_plan_ranking": ranking
    }
    # ==================================================
# STEP 6.63 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING SUMMARY
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-summary")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    risk_stock = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    risk_inventory_value = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_counts[risk_level] += 1
        risk_stock[risk_level] += product.stock
        risk_inventory_value[risk_level] += stock_value

    if risk_counts["Critical"] > 0:

        overall_priority = "Critical"
        highest_priority_risk = "Critical"
        recommended_action = "Immediate Restocking"

    elif risk_counts["High"] > 0:

        overall_priority = "High"
        highest_priority_risk = "High"
        recommended_action = "Urgent Restocking"

    elif risk_counts["Medium"] > 0:

        overall_priority = "Medium"
        highest_priority_risk = "Medium"
        recommended_action = "Monitor and Plan Restocking"

    else:

        overall_priority = "Low"
        highest_priority_risk = "Low"
        recommended_action = "No Immediate Action"

    ranking_summary = []

    ranking_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    for risk_level in ["Critical", "High", "Medium", "Low"]:

        if total_products > 0:
            percentage = round(
                (risk_counts[risk_level] / total_products) * 100,
                2
            )
        else:
            percentage = 0

        if risk_level == "Critical":

            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "High":

            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "Medium":

            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:

            action = "No Immediate Action"
            reason = "Stock level is healthy"

        ranking_summary.append({
            "rank": ranking_order[risk_level],
            "risk_level": risk_level,
            "product_count": risk_counts[risk_level],
            "percentage": percentage,
            "total_stock": risk_stock[risk_level],
            "inventory_value": risk_inventory_value[risk_level],
            "action": action,
            "reason": reason
        })

    return {
        "summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "highest_priority_risk": highest_priority_risk,
            "recommended_action": recommended_action
        },
        "ranking_summary": ranking_summary
    }
    # ==================================================
# STEP 6.64 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING DETAILS
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    ranking_order = {
        "Critical": 1,
        "High": 2,
        "Medium": 3,
        "Low": 4
    }

    ranking_details = []

    for risk_level in ["Critical", "High", "Medium", "Low"]:

        data = risk_data[risk_level]

        if total_products > 0:
            percentage = round(
                (data["product_count"] / total_products) * 100,
                2
            )
        else:
            percentage = 0

        if risk_level == "Critical":

            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"
            recommended_step = "Restock immediately and review supplier availability"

        elif risk_level == "High":

            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"
            recommended_step = "Place urgent purchase orders and increase stock"

        elif risk_level == "Medium":

            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"
            recommended_step = "Monitor sales and plan the next restocking cycle"

        else:

            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"
            recommended_step = "Continue normal inventory monitoring"

        ranking_details.append({
            "rank": ranking_order[risk_level],
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": priority,
            "action": action,
            "reason": reason,
            "recommended_step": recommended_step
        })

    return {
        "ranking_details_summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value
        },
        "risk_ranking_action_plan_details": ranking_details
    }
   # ==================================================
# STEP 6.65 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-report")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"
        elif product.stock <= 5:
            risk_level = "High"
        elif product.stock <= 10:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    ranking = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round((data["product_count"] / total_products) * 100, 2)
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":
            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"
            recommended_step = (
                "Restock immediately and review supplier availability"
            )

        elif risk_level == "High":
            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"
            recommended_step = (
                "Place urgent purchase orders and increase stock"
            )

        elif risk_level == "Medium":
            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"
            recommended_step = (
                "Monitor sales and plan the next restocking cycle"
            )

        else:
            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"
            recommended_step = (
                "Continue normal inventory monitoring"
            )

        ranking.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": priority,
            "action": action,
            "reason": reason,
            "recommended_step": recommended_step
        })

    if total_products == 0:
        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "No products available"

    elif risk_data["Critical"]["product_count"] > 0:
        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels detected"

    elif risk_data["High"]["product_count"] > 0:
        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk stock levels detected"

    elif risk_data["Medium"]["product_count"] > 0:
        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:
        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All inventory levels are healthy"

    return {
        "report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "ranking": ranking
    }
    # ==================================================
# STEP 6.66 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING SUMMARY REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-summary-report")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_summary_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if total_products == 0:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "No products available"

    elif risk_data["Critical"]["product_count"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels detected"

    elif risk_data["High"]["product_count"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk stock levels detected"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All inventory levels are healthy"

    summary = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round(
                (data["product_count"] / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "High":

            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "Medium":

            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:

            action = "No Immediate Action"
            reason = "Stock level is healthy"

        summary.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "action": action,
            "reason": reason
        })

    return {
        "summary_report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "risk_ranking_summary": summary
    }
    # ==================================================
# STEP 6.67 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING DETAILS REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-report")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if total_products == 0:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "No products available"

    elif risk_data["Critical"]["product_count"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels detected"

    elif risk_data["High"]["product_count"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk stock levels detected"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All inventory levels are healthy"

    detailed_report = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round(
                (data["product_count"] / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"
            recommended_step = (
                "Restock immediately and review supplier availability"
            )

        elif risk_level == "High":

            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"
            recommended_step = (
                "Place urgent purchase orders and increase stock"
            )

        elif risk_level == "Medium":

            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"
            recommended_step = (
                "Monitor sales and plan the next restocking cycle"
            )

        else:

            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"
            recommended_step = (
                "Continue normal inventory monitoring"
            )

        detailed_report.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": priority,
            "action": action,
            "reason": reason,
            "recommended_step": recommended_step
        })

    return {
        "details_report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "risk_ranking_details": detailed_report
    }
    # ==================================================
# STEP 6.68 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING DETAILS SUMMARY
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_counts = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    for product in products:

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_counts[risk_level] += 1

    if total_products == 0:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "No products available"

    elif risk_counts["Critical"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels detected"

    elif risk_counts["High"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk stock levels detected"

    elif risk_counts["Medium"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All inventory levels are healthy"

    ranking_summary = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        count = risk_counts[risk_level]

        percentage = (
            round((count / total_products) * 100, 2)
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":
            action = "Immediate Restocking"

        elif risk_level == "High":
            action = "Urgent Restocking"

        elif risk_level == "Medium":
            action = "Monitor and Plan Restocking"

        else:
            action = "No Immediate Action"

        ranking_summary.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": count,
            "percentage": percentage,
            "action": action
        })

    return {
        "summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "risk_ranking_summary": ranking_summary
    }
    # ==================================================
# STEP 6.69 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING DETAILS SUMMARY REPORT
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary-report")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_summary_report(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if total_products == 0:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "No products available"

    elif risk_data["Critical"]["product_count"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels detected"

    elif risk_data["High"]["product_count"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk stock levels detected"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All inventory levels are healthy"

    report = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round(
                (data["product_count"] / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "High":

            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "Medium":

            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:

            action = "No Immediate Action"
            reason = "Stock level is healthy"

        report.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "action": action,
            "reason": reason
        })

    return {
        "report_summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "risk_ranking_report": report
    }
  # ==================================================
# STEP 6.70 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING DETAILS
# SUMMARY REPORT DETAILS
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary-report-details")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_summary_report_details(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if total_products == 0:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "No products available"

    elif risk_data["Critical"]["product_count"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels detected"

    elif risk_data["High"]["product_count"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk stock levels detected"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All inventory levels are healthy"

    details = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round(
                (data["product_count"] / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"
            recommended_step = (
                "Restock immediately and review supplier availability"
            )

        elif risk_level == "High":

            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"
            recommended_step = (
                "Place urgent purchase orders and increase stock"
            )

        elif risk_level == "Medium":

            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"
            recommended_step = (
                "Monitor sales and plan the next restocking cycle"
            )

        else:

            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"
            recommended_step = (
                "Continue normal inventory monitoring"
            )

        details.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": priority,
            "action": action,
            "reason": reason,
            "recommended_step": recommended_step
        })

    return {
        "summary_report_details": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "risk_ranking_details": details
    }
    # ==================================================
# STEP 6.71 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING DETAILS
# SUMMARY REPORT RANKING
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary-report-ranking")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_summary_report_ranking(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if total_products == 0:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "No products available"

    elif risk_data["Critical"]["product_count"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels detected"

    elif risk_data["High"]["product_count"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk stock levels detected"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All inventory levels are healthy"

    ranking = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round(
                (data["product_count"] / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            action = "Immediate Restocking"

        elif risk_level == "High":

            action = "Urgent Restocking"

        elif risk_level == "Medium":

            action = "Monitor and Plan Restocking"

        else:

            action = "No Immediate Action"

        ranking.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "action": action
        })

    return {
        "ranking_summary_report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "risk_ranking": ranking
    }  
    # ==================================================
# STEP 6.72 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING DETAILS
# SUMMARY REPORT RANKING DETAILS
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary-report-ranking-details")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_summary_report_ranking_details(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if total_products == 0:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "No products available"

    elif risk_data["Critical"]["product_count"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"
        overall_reason = "Critical stock levels detected"

    elif risk_data["High"]["product_count"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"
        overall_reason = "High-risk stock levels detected"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"
        overall_reason = "Medium-risk products require monitoring"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"
        overall_reason = "All inventory levels are healthy"

    details = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round(
                (data["product_count"] / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            priority = "Critical"
            action = "Immediate Restocking"
            reason = "Products are out of stock"
            recommended_step = (
                "Restock immediately and review supplier availability"
            )

        elif risk_level == "High":

            priority = "High"
            action = "Urgent Restocking"
            reason = "Products have very low stock"
            recommended_step = (
                "Place urgent purchase orders and increase stock"
            )

        elif risk_level == "Medium":

            priority = "Medium"
            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"
            recommended_step = (
                "Monitor sales and plan the next restocking cycle"
            )

        else:

            priority = "Low"
            action = "No Immediate Action"
            reason = "Stock level is healthy"
            recommended_step = (
                "Continue normal inventory monitoring"
            )

        details.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "priority": priority,
            "action": action,
            "reason": reason,
            "recommended_step": recommended_step
        })

    return {
        "ranking_details_summary_report": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action,
            "overall_reason": overall_reason
        },
        "risk_ranking_details": details
    }
    # ==================================================
# STEP 6.73 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING
# SUMMARY REPORT RANKING
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary-report-ranking-summary")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_summary_report_ranking_summary(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    for product in products:

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level] += 1

    if risk_data["Critical"] > 0:

        overall_priority = "Critical"
        recommended_action = "Immediate Restocking"

    elif risk_data["High"] > 0:

        overall_priority = "High"
        recommended_action = "Urgent Restocking"

    elif risk_data["Medium"] > 0:

        overall_priority = "Medium"
        recommended_action = "Monitor and Plan Restocking"

    else:

        overall_priority = "Low"
        recommended_action = "No Immediate Action"

    ranking_summary = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        product_count = risk_data[risk_level]

        percentage = (
            round(
                (product_count / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            action = "Immediate Restocking"

        elif risk_level == "High":

            action = "Urgent Restocking"

        elif risk_level == "Medium":

            action = "Monitor and Plan Restocking"

        else:

            action = "No Immediate Action"

        ranking_summary.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": product_count,
            "percentage": percentage,
            "action": action
        })

    return {
        "ranking_summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "recommended_action": recommended_action
        },
        "risk_ranking_summary": ranking_summary
    }
    # ==================================================
# STEP 6.74 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING
# SUMMARY REPORT RANKING DETAILS
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary-report-ranking-details")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_summary_report_ranking_details(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if risk_data["Critical"]["product_count"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"

    elif risk_data["High"]["product_count"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"

    ranking_details = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round(
                (data["product_count"] / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "High":

            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "Medium":

            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:

            action = "No Immediate Action"
            reason = "Stock level is healthy"

        ranking_details.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "action": action,
            "reason": reason
        })

    return {
        "ranking_details_summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action
        },
        "risk_ranking_details": ranking_details
    }
    # ==================================================
# STEP 6.74 — INVENTORY DASHBOARD RISK RANKING
# DISTRIBUTION ACTION PLAN RANKING
# DETAILS SUMMARY REPORT RANKING DETAILS
# ==================================================

@app.get("/products/inventory-dashboard-risk-ranking-distribution-action-plan-ranking-details-summary-report-ranking-details")
def get_inventory_dashboard_risk_ranking_distribution_action_plan_ranking_details_summary_report_ranking_details(
    db: Session = Depends(get_db)
):

    products = db.query(Product).all()

    total_products = len(products)

    total_stock = sum(
        product.stock
        for product in products
    )

    total_inventory_value = sum(
        product.price * product.stock
        for product in products
    )

    risk_data = {
        "Critical": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "High": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Medium": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        },
        "Low": {
            "product_count": 0,
            "total_stock": 0,
            "inventory_value": 0
        }
    }

    for product in products:

        stock_value = product.price * product.stock

        if product.stock == 0:
            risk_level = "Critical"

        elif product.stock <= 5:
            risk_level = "High"

        elif product.stock <= 10:
            risk_level = "Medium"

        else:
            risk_level = "Low"

        risk_data[risk_level]["product_count"] += 1
        risk_data[risk_level]["total_stock"] += product.stock
        risk_data[risk_level]["inventory_value"] += stock_value

    if risk_data["Critical"]["product_count"] > 0:

        overall_priority = "Critical"
        overall_action = "Immediate Restocking"

    elif risk_data["High"]["product_count"] > 0:

        overall_priority = "High"
        overall_action = "Urgent Restocking"

    elif risk_data["Medium"]["product_count"] > 0:

        overall_priority = "Medium"
        overall_action = "Monitor and Plan Restocking"

    else:

        overall_priority = "Low"
        overall_action = "No Immediate Action"

    ranking_details = []

    risk_order = [
        ("Critical", 1),
        ("High", 2),
        ("Medium", 3),
        ("Low", 4)
    ]

    for risk_level, rank in risk_order:

        data = risk_data[risk_level]

        percentage = (
            round(
                (data["product_count"] / total_products) * 100,
                2
            )
            if total_products > 0
            else 0
        )

        if risk_level == "Critical":

            action = "Immediate Restocking"
            reason = "Products are out of stock"

        elif risk_level == "High":

            action = "Urgent Restocking"
            reason = "Products have very low stock"

        elif risk_level == "Medium":

            action = "Monitor and Plan Restocking"
            reason = "Product stock needs monitoring"

        else:

            action = "No Immediate Action"
            reason = "Stock level is healthy"

        ranking_details.append({
            "rank": rank,
            "risk_level": risk_level,
            "product_count": data["product_count"],
            "percentage": percentage,
            "total_stock": data["total_stock"],
            "inventory_value": data["inventory_value"],
            "action": action,
            "reason": reason
        })

    return {
        "ranking_details_summary": {
            "total_products": total_products,
            "total_stock": total_stock,
            "total_inventory_value": total_inventory_value,
            "overall_priority": overall_priority,
            "overall_action": overall_action
        },
        "risk_ranking_details": ranking_details
    }
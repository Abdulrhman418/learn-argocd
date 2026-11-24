import os

import psycopg
from flask import Flask, jsonify, request
from psycopg.rows import dict_row

app = Flask(__name__)


def connect_to_database():
    connection = psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=3,
        row_factory=dict_row,
    )
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL CHECK (char_length(name) <= 120),
                description TEXT NOT NULL DEFAULT '',
                price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    connection.commit()
    return connection


def serialize_product(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "price": float(row["price"]),
        "created_at": row["created_at"].isoformat(),
    }


@app.get("/livez")
def live():
    return jsonify(status="alive")


@app.get("/readyz")
def ready():
    try:
        with connect_to_database():
            pass
        return jsonify(status="ready")
    except psycopg.Error:
        app.logger.exception("Database readiness check failed")
        return jsonify(error="Database is not ready"), 503


@app.get("/api/products")
def list_products():
    try:
        with connect_to_database() as connection:
            rows = connection.execute(
                "SELECT id, name, description, price, created_at "
                "FROM products ORDER BY id DESC"
            ).fetchall()
        return jsonify(products=[serialize_product(row) for row in rows])
    except psycopg.Error:
        app.logger.exception("Could not load products")
        return jsonify(error="Database is unavailable"), 503


@app.post("/api/products")
def create_product():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="A JSON product is required"), 400

    name = payload.get("name", "").strip() if isinstance(payload.get("name"), str) else ""
    description = (
        payload.get("description", "").strip()
        if isinstance(payload.get("description", ""), str)
        else ""
    )
    price = payload.get("price")
    if not name or len(name) > 120:
        return jsonify(error="Product name must be 1-120 characters"), 400
    if len(description) > 500:
        return jsonify(error="Description must be 500 characters or fewer"), 400
    try:
        price = float(price)
    except (TypeError, ValueError):
        return jsonify(error="Price must be a non-negative number"), 400
    if not 0 <= price < 100000000:
        return jsonify(error="Price must be a non-negative amount"), 400

    try:
        with connect_to_database() as connection:
            row = connection.execute(
                """
                INSERT INTO products (name, description, price)
                VALUES (%s, %s, %s)
                RETURNING id, name, description, price, created_at
                """,
                (name, description, price),
            ).fetchone()
        return jsonify(product=serialize_product(row)), 201
    except psycopg.Error:
        app.logger.exception("Could not create product")
        return jsonify(error="Database is unavailable"), 503


@app.delete("/api/products/<int:product_id>")
def delete_product(product_id):
    try:
        with connect_to_database() as connection:
            result = connection.execute(
                "DELETE FROM products WHERE id = %s RETURNING id",
                (product_id,),
            ).fetchone()
        if result is None:
            return jsonify(error="Product not found"), 404
        return "", 204
    except psycopg.Error:
        app.logger.exception("Could not delete product")
        return jsonify(error="Database is unavailable"), 503

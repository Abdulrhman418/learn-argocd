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
            CREATE TABLE IF NOT EXISTS notes (
                id BIGSERIAL PRIMARY KEY,
                content TEXT NOT NULL CHECK (char_length(content) <= 500),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    connection.commit()
    return connection


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


@app.get("/api/notes")
def list_notes():
    try:
        with connect_to_database() as connection:
            rows = connection.execute(
                "SELECT id, content, created_at FROM notes ORDER BY id DESC"
            ).fetchall()
        return jsonify(
            notes=[
                {
                    "id": row["id"],
                    "content": row["content"],
                    "created_at": row["created_at"].isoformat(),
                }
                for row in rows
            ]
        )
    except psycopg.Error:
        app.logger.exception("Could not load notes")
        return jsonify(error="Database is unavailable"), 503


@app.post("/api/notes")
def create_note():
    payload = request.get_json(silent=True)
    content = payload.get("content", "").strip() if isinstance(payload, dict) else ""
    if not content:
        return jsonify(error="Note content is required"), 400
    if len(content) > 500:
        return jsonify(error="Note content must be 500 characters or fewer"), 400

    try:
        with connect_to_database() as connection:
            row = connection.execute(
                "INSERT INTO notes (content) VALUES (%s) "
                "RETURNING id, content, created_at",
                (content,),
            ).fetchone()
        return jsonify(
            note={
                "id": row["id"],
                "content": row["content"],
                "created_at": row["created_at"].isoformat(),
            }
        ), 201
    except psycopg.Error:
        app.logger.exception("Could not create note")
        return jsonify(error="Database is unavailable"), 503


@app.delete("/api/notes/<int:note_id>")
def delete_note(note_id):
    try:
        with connect_to_database() as connection:
            result = connection.execute(
                "DELETE FROM notes WHERE id = %s RETURNING id",
                (note_id,),
            ).fetchone()
        if result is None:
            return jsonify(error="Note not found"), 404
        return "", 204
    except psycopg.Error:
        app.logger.exception("Could not delete note")
        return jsonify(error="Database is unavailable"), 503

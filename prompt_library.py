"""prompt_library.py — Curated prompt catalog and custom prompt management.

Supports:
- Category filtering (Business, Marketing, Social Media, Photography, Cinematic, Education, Programming, Creative Writing)
- Search across titles, tags, and prompt content
- Favoriting prompts
- User-created custom prompts
"""

from __future__ import annotations

import sqlite3
from typing import List, Dict, Any, Optional
import database

CATEGORIES = [
    "All",
    "Business",
    "Marketing",
    "Social Media",
    "Photography",
    "Cinematic",
    "Education",
    "Programming",
    "Creative Writing",
]


def get_prompts(
    category: str = "All",
    search_query: str = "",
    user_id: Optional[int] = None,
    only_favorites: bool = False,
) -> List[Dict[str, Any]]:
    """Retrieve prompt templates matching category, search term, and favorites."""
    conn = database.get_db_connection()
    try:
        query = "SELECT id, category, title, prompt, description, tags, is_custom, user_id, is_favorite, created_at FROM prompt_templates WHERE 1=1"
        params: list[Any] = []

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        if search_query.strip():
            like_term = f"%{search_query.strip()}%"
            query += " AND (title LIKE ? OR prompt LIKE ? OR tags LIKE ? OR description LIKE ?)"
            params.extend([like_term, like_term, like_term, like_term])

        if only_favorites:
            query += " AND is_favorite = 1"

        query += " ORDER BY is_favorite DESC, created_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def add_custom_prompt(
    user_id: int,
    category: str,
    title: str,
    prompt: str,
    description: str = "",
    tags: str = "",
) -> int:
    """Create a user-owned custom prompt template."""
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO prompt_templates (category, title, prompt, description, tags, is_custom, user_id, is_favorite)
            VALUES (?, ?, ?, ?, ?, 1, ?, 0)
            """,
            (category, title.strip(), prompt.strip(), description.strip(), tags.strip(), user_id),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def toggle_favorite_prompt(prompt_id: int) -> bool:
    """Toggle favorite status of a prompt template."""
    conn = database.get_db_connection()
    try:
        row = conn.execute("SELECT is_favorite FROM prompt_templates WHERE id = ?", (prompt_id,)).fetchone()
        if not row:
            return False
        new_fav = 0 if row["is_favorite"] == 1 else 1
        conn.execute("UPDATE prompt_templates SET is_favorite = ? WHERE id = ?", (new_fav, prompt_id))
        conn.commit()
        return bool(new_fav)
    finally:
        conn.close()


def delete_custom_prompt(prompt_id: int, user_id: int) -> bool:
    """Delete a custom prompt owned by user."""
    conn = database.get_db_connection()
    try:
        res = conn.execute("DELETE FROM prompt_templates WHERE id = ? AND is_custom = 1 AND user_id = ?", (prompt_id, user_id))
        conn.commit()
        return res.rowcount > 0
    finally:
        conn.close()

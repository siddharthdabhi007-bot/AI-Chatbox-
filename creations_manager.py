"""creations_manager.py — Management of user-generated creations (Text, Audio, Image, Video).

Handles:
- Storing creation metadata with user ownership
- Filtering by type, date, search keyword, and favorites
- Deletion with file cleanup
- Updating titles and favorite status
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import database


def save_creation(
    user_id: int,
    creation_type: str,  # 'text', 'audio', 'image', 'video'
    title: str,
    prompt: str,
    model_used: str,
    file_path: str = "",
    content_preview: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    negative_prompt: str = "",
) -> int:
    """Save a newly generated creation record to the database."""
    conn = database.get_db_connection()
    try:
        cursor = conn.cursor()
        meta_str = json.dumps(metadata or {})
        cursor.execute(
            """
            INSERT INTO creations (
                user_id, creation_type, title, prompt, negative_prompt,
                model_used, file_path, content_preview, metadata_json, is_favorite
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                creation_type,
                title.strip() or f"Untitled {creation_type.title()}",
                prompt.strip(),
                negative_prompt.strip(),
                model_used,
                file_path,
                content_preview[:500],
                meta_str,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_creations(
    user_id: int,
    creation_type: str = "All",  # 'All', 'text', 'audio', 'image', 'video'
    search_query: str = "",
    only_favorites: bool = False,
    sort_order: str = "Newest",  # 'Newest', 'Oldest', 'Title'
) -> List[Dict[str, Any]]:
    """Query user creations with filtering and search."""
    conn = database.get_db_connection()
    try:
        query = "SELECT * FROM creations WHERE user_id = ?"
        params: list[Any] = [user_id]

        if creation_type and creation_type.lower() != "all":
            query += " AND LOWER(creation_type) = ?"
            params.append(creation_type.lower())

        if search_query.strip():
            like_term = f"%{search_query.strip()}%"
            query += " AND (title LIKE ? OR prompt LIKE ? OR content_preview LIKE ?)"
            params.extend([like_term, like_term, like_term])

        if only_favorites:
            query += " AND is_favorite = 1"

        if sort_order == "Oldest":
            query += " ORDER BY created_at ASC"
        elif sort_order == "Title":
            query += " ORDER BY title ASC"
        else:
            query += " ORDER BY created_at DESC"

        rows = conn.execute(query, params).fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["metadata"] = json.loads(d["metadata_json"])
            except Exception:
                d["metadata"] = {}
            results.append(d)
        return results
    finally:
        conn.close()


def toggle_favorite_creation(creation_id: int, user_id: int) -> bool:
    """Toggle favorite status of a creation."""
    conn = database.get_db_connection()
    try:
        row = conn.execute("SELECT is_favorite FROM creations WHERE id = ? AND user_id = ?", (creation_id, user_id)).fetchone()
        if not row:
            return False
        new_fav = 0 if row["is_favorite"] == 1 else 1
        conn.execute("UPDATE creations SET is_favorite = ? WHERE id = ?", (new_fav, creation_id))
        conn.commit()
        return bool(new_fav)
    finally:
        conn.close()


def delete_creation(creation_id: int, user_id: int) -> bool:
    """Delete creation record and its underlying disk file if applicable."""
    conn = database.get_db_connection()
    try:
        row = conn.execute("SELECT file_path FROM creations WHERE id = ? AND user_id = ?", (creation_id, user_id)).fetchone()
        if not row:
            return False

        file_path = row["file_path"]
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        conn.execute("DELETE FROM creations WHERE id = ? AND user_id = ?", (creation_id, user_id))
        conn.commit()
        return True
    finally:
        conn.close()


def update_creation_title(creation_id: int, user_id: int, new_title: str) -> bool:
    """Update title of a user creation."""
    conn = database.get_db_connection()
    try:
        res = conn.execute("UPDATE creations SET title = ? WHERE id = ? AND user_id = ?", (new_title.strip(), creation_id, user_id))
        conn.commit()
        return res.rowcount > 0
    finally:
        conn.close()

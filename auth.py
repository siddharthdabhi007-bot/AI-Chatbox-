"""auth.py — User authentication, password hashing, and session management.

Provides secure login, user registration, role verification, and session state tracking.
"""

from __future__ import annotations

import hashlib
import sqlite3
from typing import Optional, Dict, Any
import database


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = "ai_creative_studio_secret_salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against stored hash."""
    return hash_password(plain_password) == hashed_password


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user with email and password."""
    conn = database.get_db_connection()
    try:
        user = conn.execute(
            "SELECT id, username, email, password_hash, role, credit_balance, plan_name FROM users WHERE email = ?",
            (email.strip().lower(),),
        ).fetchone()

        if user and verify_password(password, user["password_hash"]):
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "credit_balance": user["credit_balance"],
                "plan_name": user["plan_name"],
            }
        return None
    finally:
        conn.close()


def register_user(username: str, email: str, password: str) -> tuple[bool, str, Optional[Dict[str, Any]]]:
    """Register a new user account with default starting credits."""
    email = email.strip().lower()
    username = username.strip()

    if not username or not email or len(password) < 6:
        return False, "Username, email, and password (min 6 characters) are required.", None

    conn = database.get_db_connection()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ? OR username = ?",
            (email, username),
        ).fetchone()
        if existing:
            return False, "An account with that email or username already exists.", None

        pw_hash = hash_password(password)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, email, password_hash, role, credit_balance, plan_name)
            VALUES (?, ?, ?, 'creator', 100, 'Starter Free')
            """,
            (username, email, pw_hash),
        )
        new_id = cursor.lastrowid
        conn.commit()

        return True, "Account created successfully!", {
            "id": new_id,
            "username": username,
            "email": email,
            "role": "creator",
            "credit_balance": 100,
            "plan_name": "Starter Free",
        }
    except Exception as exc:
        return False, f"Registration error: {str(exc)}", None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user account info by ID."""
    conn = database.get_db_connection()
    try:
        row = conn.execute(
            "SELECT id, username, email, role, credit_balance, plan_name FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_default_creator_user() -> Dict[str, Any]:
    """Return default seeded user for instant seamless experience."""
    conn = database.get_db_connection()
    try:
        row = conn.execute("SELECT id, username, email, role, credit_balance, plan_name FROM users LIMIT 1").fetchone()
        if row:
            return dict(row)
        return {
            "id": 1,
            "username": "StudioCreator",
            "email": "creator@aicreative.studio",
            "role": "creator",
            "credit_balance": 250,
            "plan_name": "Creator Pro",
        }
    finally:
        conn.close()

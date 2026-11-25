"""credit_manager.py — Secure credit billing and transactional ledger.

Ensures:
- Atomic credit deduction and verification on backend
- Negative balance prevention
- Instant automatic refunds for failed generation jobs
- Transaction audit trail logging
"""

from __future__ import annotations

import sqlite3
from typing import Tuple, Optional, Dict, Any, List
import database

# Credit Cost Policy
COST_TEXT_GEN = 1      # 1 credit per AI text/script generation
COST_SPEECH_GEN = 2    # 2 credits per high-quality speech generation
COST_IMAGE_GEN = 5     # 5 credits per FLUX.1 image
COST_VIDEO_GEN = 25    # 25 credits per Wan 2.7 video


def get_user_credits(user_id: int) -> int:
    """Retrieve current verified credit balance for a user."""
    conn = database.get_db_connection()
    try:
        row = conn.execute("SELECT credit_balance FROM users WHERE id = ?", (user_id,)).fetchone()
        return int(row["credit_balance"]) if row else 0
    finally:
        conn.close()


def deduct_credits(
    user_id: int,
    amount: int,
    description: str,
) -> Tuple[bool, str, int]:
    """Atomically check balance and deduct credits inside an exclusive transaction.

    Returns:
        (success: bool, message: str, new_balance: int)
    """
    if amount <= 0:
        return True, "No credits required.", get_user_credits(user_id)

    conn = database.get_db_connection()
    try:
        conn.execute("BEGIN IMMEDIATE;")
        user = conn.execute("SELECT credit_balance FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.rollback()
            return False, "User account not found.", 0

        current_balance = int(user["credit_balance"])
        if current_balance < amount:
            conn.rollback()
            return (
                False,
                f"Insufficient credits. Required: {amount}, Available: {current_balance}.",
                current_balance,
            )

        new_balance = current_balance - amount
        conn.execute(
            "UPDATE users SET credit_balance = ? WHERE id = ?",
            (new_balance, user_id),
        )
        conn.execute(
            """
            INSERT INTO credit_transactions (user_id, amount, balance_after, transaction_type, description)
            VALUES (?, ?, ?, 'deduction', ?)
            """,
            (user_id, -amount, new_balance, description),
        )
        conn.commit()
        return True, "Credits deducted successfully.", new_balance
    except Exception as exc:
        conn.rollback()
        return False, f"Transaction error: {str(exc)}", 0
    finally:
        conn.close()


def refund_credits(
    user_id: int,
    amount: int,
    reason: str,
) -> Tuple[bool, str, int]:
    """Atomically refund credits back to a user account when a generation job fails."""
    if amount <= 0:
        return True, "No credits to refund.", get_user_credits(user_id)

    conn = database.get_db_connection()
    try:
        conn.execute("BEGIN IMMEDIATE;")
        user = conn.execute("SELECT credit_balance FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.rollback()
            return False, "User account not found.", 0

        new_balance = int(user["credit_balance"]) + amount
        conn.execute(
            "UPDATE users SET credit_balance = ? WHERE id = ?",
            (new_balance, user_id),
        )
        conn.execute(
            """
            INSERT INTO credit_transactions (user_id, amount, balance_after, transaction_type, description)
            VALUES (?, ?, ?, 'refund', ?)
            """,
            (user_id, amount, new_balance, f"Refund: {reason}"),
        )
        conn.commit()
        return True, "Credits refunded.", new_balance
    except Exception as exc:
        conn.rollback()
        return False, f"Refund transaction error: {str(exc)}", 0
    finally:
        conn.close()


def grant_credits(
    user_id: int,
    amount: int,
    description: str = "Plan upgrade or bonus",
) -> Tuple[bool, str, int]:
    """Grant additional credits (e.g. monthly subscription replenishment or plan purchase)."""
    conn = database.get_db_connection()
    try:
        conn.execute("BEGIN IMMEDIATE;")
        user = conn.execute("SELECT credit_balance FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.rollback()
            return False, "User account not found.", 0

        new_balance = int(user["credit_balance"]) + amount
        conn.execute(
            "UPDATE users SET credit_balance = ? WHERE id = ?",
            (new_balance, user_id),
        )
        conn.execute(
            """
            INSERT INTO credit_transactions (user_id, amount, balance_after, transaction_type, description)
            VALUES (?, ?, ?, 'subscription_grant', ?)
            """,
            (user_id, amount, new_balance, description),
        )
        conn.commit()
        return True, f"Granted {amount} credits.", new_balance
    except Exception as exc:
        conn.rollback()
        return False, f"Grant error: {str(exc)}", 0
    finally:
        conn.close()


def get_transaction_history(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent credit transaction ledger for auditing and user visibility."""
    conn = database.get_db_connection()
    try:
        rows = conn.execute(
            """
            SELECT id, amount, balance_after, transaction_type, description, created_at
            FROM credit_transactions
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

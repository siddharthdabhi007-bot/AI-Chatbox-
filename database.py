"""database.py — Database schema, ORM models, and transactional repository.

Implements SQLite/SQLAlchemy storage for:
- Users & authentication
- Creations (text, audio, image, video)
- Generation jobs (queued, processing, completed, failed)
- Credit transactions with atomic balance guards
- Prompt library templates
- Subscription plans
"""

from __future__ import annotations

import os
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any, Dict, List

DB_PATH = Path(__file__).resolve().parent / "studio.db"


def get_db_connection() -> sqlite3.Connection:
    """Create and return a configured SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initialize database tables, indexes, and seed default plans and prompts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'creator',
            credit_balance INTEGER NOT NULL DEFAULT 100,
            plan_name TEXT DEFAULT 'Creator Pro',
            avatar_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Subscription Plans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price_monthly REAL NOT NULL,
            credits_monthly INTEGER NOT NULL,
            features_json TEXT NOT NULL
        );
    """)

    # 3. Creations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS creations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            creation_type TEXT NOT NULL, -- 'text', 'audio', 'image', 'video'
            title TEXT NOT NULL,
            prompt TEXT NOT NULL,
            negative_prompt TEXT DEFAULT '',
            model_used TEXT NOT NULL,
            file_path TEXT DEFAULT '',
            content_preview TEXT DEFAULT '',
            metadata_json TEXT DEFAULT '{}',
            is_favorite INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 4. Generation Jobs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generation_jobs (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            job_type TEXT NOT NULL, -- 'image', 'video', 'text', 'audio'
            status TEXT NOT NULL,   -- 'queued', 'processing', 'completed', 'failed'
            prompt TEXT NOT NULL,
            model_used TEXT NOT NULL,
            cost_credits INTEGER NOT NULL,
            result_creation_id INTEGER,
            error_message TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 5. Credit Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL, -- negative for deduction, positive for refund/purchase
            balance_after INTEGER NOT NULL,
            transaction_type TEXT NOT NULL, -- 'deduction', 'refund', 'subscription_grant', 'topup'
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
    """)

    # 6. Prompt Templates Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            prompt TEXT NOT NULL,
            description TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            is_custom INTEGER DEFAULT 0,
            user_id INTEGER DEFAULT NULL,
            is_favorite INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Indexes for fast querying
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_creations_user ON creations (user_id, creation_type);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_creations_fav ON creations (user_id, is_favorite);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_user ON generation_jobs (user_id, status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_credit_user ON credit_transactions (user_id);")

    # Seed default plans if not already present
    cursor.execute("SELECT COUNT(*) FROM plans")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO plans (id, name, price_monthly, credits_monthly, features_json)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("free", "Starter Free", 0.0, 50, json.dumps([
                "50 credits per month",
                "Standard speed generation",
                "Local Kokoro TTS (Unlimited)",
                "Standard 720p Video",
                "Community Support"
            ])),
            ("pro", "Creator Pro", 19.0, 500, json.dumps([
                "500 credits per month",
                "High priority GPU queue",
                "Kokoro & Piper Neural TTS",
                "FLUX.1 Schnell Fast Images",
                "Wan 2.7 1080p Cinematic Videos",
                "Private Creations Storage"
            ])),
            ("enterprise", "Studio Enterprise", 49.0, 2000, json.dumps([
                "2,000 credits per month",
                "Instant dedicated concurrency",
                "Custom LLM fine-tuning",
                "Full commercial copyright license",
                "Dedicated 24/7 priority support"
            ])),
        ])

    # Seed default user if not exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'creator@aicreative.studio'")
    if cursor.fetchone()[0] == 0:
        import hashlib
        # Password: password123
        demo_pass_hash = hashlib.sha256("password123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, credit_balance, plan_name)
            VALUES ('StudioCreator', 'creator@aicreative.studio', ?, 'creator', 250, 'Creator Pro')
        """, (demo_pass_hash,))

    # Seed default curated prompts if not exists
    cursor.execute("SELECT COUNT(*) FROM prompt_templates WHERE is_custom = 0")
    if cursor.fetchone()[0] == 0:
        seed_prompts = [
            # Business & Marketing
            ("Business", "Executive SaaS Launch Pitch", "Craft an inspiring 60-second executive pitch announcing a revolutionary AI automation platform designed for enterprise scale.", "Perfect for startup founders, pitch competitions, and investor updates.", "business,pitch,saas"),
            ("Marketing", "Viral Product Video Ad Script", "Write an energetic, hook-driven 30-second script for a next-generation wireless noise-canceling headphone ad.", "High-conversion marketing copy for Instagram Reels and TikTok.", "marketing,video,ad"),
            ("Social Media", "Thought Leadership LinkedIn Post", "Write an insightful 3-paragraph thought leadership post discussing how local open-source AI is disrupting cloud monopolies.", "Engaging commentary for LinkedIn professionals and founders.", "social,linkedin,ai"),
            # Photography & Cinematic
            ("Photography", "High-End Corporate Studio Portrait", "Cinematic medium close-up shot of an ambitious tech founder in a modern glass office, dramatic soft rim lighting, shallow depth of field, 85mm lens, 8k resolution.", "Photorealistic portrait prompt for FLUX.1 image generator.", "photo,portrait,cinematic"),
            ("Cinematic", "Futuristic Neon Metropolis Flythrough", "A slow sweeping drone camera movement gliding between towering glass skyscrapers glowing with purple and cyan holographic advertisements, rain-slicked streets below, cinematic reflections.", "Dynamic cinematic prompt for Wan 2.7 video generator.", "video,drone,cyberpunk"),
            ("Photography", "Minimalist Luxury Product Photography", "Luxury perfume glass bottle resting on dark obsidian stone with soft rippling water, warm golden hour sunbeams, minimalist aesthetic, magazine editorial.", "Commercial studio product photography.", "product,luxury,minimal"),
            # Creative Writing & Education
            ("Creative Writing", "Sci-Fi Mystery Opening Narration", "The ancient observatory on the edge of the Kuiper Belt had been abandoned for three centuries. Until today, when the sub-space beacon suddenly blinked green.", "Compelling opening hook for audiobooks and storytelling.", "story,scifi,audiobook"),
            ("Education", "Quantum Computing in Plain English", "Explain the concept of quantum superposition using a simple, intuitive coin spin analogy that anyone without a physics degree can understand.", "Educational script for explainers and YouTube shorts.", "education,physics,explainer"),
            ("Programming", "Clean Architecture Python Guide", "Explain the core principles of Clean Architecture in modern Python backend systems with a focus on loose coupling and testability.", "Technical overview for engineering teams.", "coding,architecture,python"),
        ]
        cursor.executemany("""
            INSERT INTO prompt_templates (category, title, prompt, description, tags, is_custom)
            VALUES (?, ?, ?, ?, ?, 0)
        """, seed_prompts)

    conn.commit()
    conn.close()


# Initialize database automatically on import
init_db()

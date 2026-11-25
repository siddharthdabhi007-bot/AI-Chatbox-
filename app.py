"""app.py — Master SaaS Application Controller for AI Creative Studio.

Upgrades the existing application into an enterprise-grade AI Creative Studio:
- ChatGPT / Canva / Leonardo AI inspired SaaS UI
- Complete Sidebar & Top Navigation
- AI Text & Script Generator (Ollama)
- AI Speech Generator (Kokoro-82M & Piper Neural TTS)
- AI Image Generator (FLUX.1 Schnell)
- AI Video Generator (Wan 2.7)
- Central 'My Creations' Library
- Curated Prompt Library
- Real-time Credit Management & Subscription Tiers
- Settings & API Key Management
"""

from __future__ import annotations

import os
import streamlit as st
from dotenv import load_dotenv

# Database, Auth & Credit systems
import database
import auth
import credit_manager
import creations_manager
import prompt_library
import ui_theme

# Views
from views.dashboard import render_dashboard
from views.text_generator import render_text_generator
from views.speech_generator import render_speech_generator
from views.image_generator import render_image_generator
from views.video_generator import render_video_generator
from views.my_creations import render_my_creations
from views.prompt_library_view import render_prompt_library
from views.credits_view import render_credits_view
from views.settings_view import render_settings

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Studio.AI — AI Creative Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session State
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"

if "current_user" not in st.session_state:
    st.session_state["current_user"] = auth.get_default_creator_user()

if "nav_selection" not in st.session_state:
    st.session_state["nav_selection"] = "Dashboard"

user = st.session_state["current_user"]
user_id = user["id"]
is_dark = st.session_state["theme_mode"] == "Dark"

# Inject Custom SaaS CSS & Fonts
st.markdown(ui_theme.get_theme_css(is_dark=is_dark), unsafe_allow_html=True)


# ---------------- SIDEBAR NAVIGATION ----------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1rem 0; display: flex; align-items: center; gap: 0.6rem;">
            <span style="font-size: 1.6rem; font-weight: 800; background: linear-gradient(135deg, #8B5CF6, #6366F1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Studio.AI
            </span>
            <span class="saas-pill pill-violet" style="font-size: 0.7rem;">PRO</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_options = [
        "Dashboard",
        "AI Text Generator",
        "AI Speech Generator",
        "AI Image Generator",
        "AI Video Generator",
        "My Creations",
        "Prompt Library",
        "Usage & Credits",
        "Settings",
    ]

    icons_map = {
        "Dashboard": "📊",
        "AI Text Generator": "✍️",
        "AI Speech Generator": "🎙️",
        "AI Image Generator": "🖼️",
        "AI Video Generator": "🎬",
        "My Creations": "📁",
        "Prompt Library": "📚",
        "Usage & Credits": "💳",
        "Settings": "⚙️",
    }

    # Format nav options with icons
    formatted_options = [f"{icons_map[opt]} {opt}" for opt in nav_options]

    # Find index of current nav_selection
    current_idx = 0
    for i, opt in enumerate(nav_options):
        if opt == st.session_state["nav_selection"]:
            current_idx = i
            break

    selected_formatted = st.radio(
        "Navigation",
        formatted_options,
        index=current_idx,
        label_visibility="collapsed",
    )

    # Update state from radio selection
    selected_clean = selected_formatted.split(" ", 1)[1]
    if selected_clean != st.session_state["nav_selection"]:
        st.session_state["nav_selection"] = selected_clean
        st.rerun()

    st.divider()

    # Credit balance widget in sidebar
    verified_credits = credit_manager.get_user_credits(user_id)
    st.markdown(
        f"""
        <div class="saas-card" style="padding: 0.9rem; margin-bottom: 0.8rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.82rem; color: #94A3B8;">CREDIT BALANCE</span>
                <span class="saas-pill pill-emerald">{verified_credits}</span>
            </div>
            <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.4rem;">
                Tier: <b>{user.get('plan_name', 'Creator Pro')}</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("⚡ Upgrade Plan / Add Credits", use_container_width=True):
        st.session_state["nav_selection"] = "Usage & Credits"
        st.rerun()

    st.divider()

    # Quick Theme Switcher
    theme_choice = st.selectbox(
        "Theme Mode",
        ["Dark", "Light"],
        index=0 if is_dark else 1,
        label_visibility="collapsed",
    )
    if theme_choice != st.session_state["theme_mode"]:
        st.session_state["theme_mode"] = theme_choice
        st.rerun()


# ---------------- TOP NAVIGATION BAR ----------------
verified_credits = credit_manager.get_user_credits(user_id)
ui_theme.render_top_navbar(
    user_dict=user,
    current_page=st.session_state["nav_selection"],
    credit_balance=verified_credits,
)


# ---------------- ROUTER ----------------
current_page = st.session_state["nav_selection"]

if current_page == "Dashboard":
    render_dashboard(user_id=user_id, user_dict=user)

elif current_page == "AI Text Generator":
    render_text_generator(user_id=user_id, user_dict=user)

elif current_page == "AI Speech Generator":
    render_speech_generator(user_id=user_id, user_dict=user)

elif current_page == "AI Image Generator":
    render_image_generator(user_id=user_id, user_dict=user)

elif current_page == "AI Video Generator":
    render_video_generator(user_id=user_id, user_dict=user)

elif current_page == "My Creations":
    render_my_creations(user_id=user_id, user_dict=user)

elif current_page == "Prompt Library":
    render_prompt_library(user_id=user_id, user_dict=user)

elif current_page == "Usage & Credits":
    render_credits_view(user_id=user_id, user_dict=user)

elif current_page == "Settings":
    render_settings(user_id=user_id, user_dict=user)

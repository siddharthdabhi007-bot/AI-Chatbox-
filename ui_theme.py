"""ui_theme.py — Premium SaaS Design System, CSS styles, and UI Components.

Color Palette:
- Deep navy background: #0B0D17
- Card background: #151827
- Border color: #23273D
- Primary violet: #8B5CF6
- Indigo accent: #6366F1
- Text primary: #F8FAFC
- Text secondary: #94A3B8
"""

from __future__ import annotations

import streamlit as st

ICONS = {
    "dashboard": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    "text": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 6.1H3"/><path d="M21 12.1H3"/><path d="M15.1 18H3"/></svg>',
    "image": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>',
    "video": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 8-6 4 6 4V8Z"/><rect width="14" height="12" x="2" y="6" rx="2"/></svg>',
    "audio": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>',
    "folder": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>',
    "library": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 6 4 14"/><path d="M12 6v14"/><path d="M8 8v12"/><path d="M4 4v16"/></svg>',
    "history": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>',
    "star": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    "credit": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/></svg>',
    "settings": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
    "sparkles": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M19 17v4"/><path d="M3 5h4"/><path d="M17 19h4"/></svg>',
    "help": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>',
}


def get_icon(name: str) -> str:
    """Return inline SVG for requested icon name."""
    return ICONS.get(name.lower(), ICONS["sparkles"])


def get_theme_css(is_dark: bool = True) -> str:
    """Return complete SaaS CSS stylesheet for dark and light modes."""
    if is_dark:
        bg_main = "#0B0D17"
        bg_card = "#151827"
        border = "#23273D"
        text_primary = "#F8FAFC"
        text_muted = "#94A3B8"
        input_bg = "#111422"
    else:
        bg_main = "#F8FAFC"
        bg_card = "#FFFFFF"
        border = "#E2E8F0"
        text_primary = "#0F172A"
        text_muted = "#64748B"
        input_bg = "#F1F5F9"

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global reset and typography */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background-color: {bg_main} !important;
        color: {text_primary} !important;
    }}

    /* Header styling */
    .saas-header {{
        padding: 0.8rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid {border};
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}

    /* Card containers */
    .saas-card {{
        background-color: {bg_card} !important;
        border: 1px solid {border} !important;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }}
    .saas-card:hover {{
        border-color: #8B5CF6;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.08);
    }}

    /* Stat & Metric widget */
    .stat-card {{
        background-color: {bg_card};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 1rem 1.25rem;
        display: flex;
        flex-direction: column;
    }}
    .stat-label {{
        font-size: 0.82rem;
        font-weight: 500;
        color: {text_muted};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }}
    .stat-value {{
        font-size: 1.85rem;
        font-weight: 700;
        color: {text_primary};
        line-height: 1.2;
    }}
    .stat-desc {{
        font-size: 0.8rem;
        color: {text_muted};
        margin-top: 0.25rem;
    }}

    /* Badges & Pills */
    .saas-pill {{
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.65rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }}
    .pill-violet {{ background-color: rgba(139, 92, 246, 0.15); color: #C4B5FD; border: 1px solid rgba(139, 92, 246, 0.3); }}
    .pill-emerald {{ background-color: rgba(16, 185, 129, 0.15); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .pill-amber {{ background-color: rgba(245, 158, 11, 0.15); color: #FCD34D; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .pill-indigo {{ background-color: rgba(99, 102, 241, 0.15); color: #A5B4FC; border: 1px solid rgba(99, 102, 241, 0.3); }}

    /* Primary buttons */
    .stButton > button[kind="primary"], .stButton > button:first-child {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }}

    /* Inputs and forms */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {{
        background-color: {input_bg} !important;
        border: 1px solid {border} !important;
        color: {text_primary} !important;
        border-radius: 8px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }}

    /* Empty states */
    .empty-state {{
        text-align: center;
        padding: 3rem 1.5rem;
        border: 2px dashed {border};
        border-radius: 12px;
        margin: 1rem 0;
    }}
    .empty-icon {{
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #8B5CF6;
    }}
    .empty-title {{
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }}
    .empty-desc {{
        color: {text_muted};
        font-size: 0.88rem;
        max-width: 400px;
        margin: 0 auto 1rem auto;
    }}
    </style>
    """


def render_top_navbar(user_dict: dict, current_page: str, credit_balance: int) -> None:
    """Render top SaaS navigation bar with credit balance, user plan, and profile."""
    col1, col2, col3 = st.columns([4, 2, 2])
    with col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 0.6rem;">
                <span style="font-size: 1.4rem; font-weight: 800; background: linear-gradient(135deg, #8B5CF6, #6366F1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Studio.AI
                </span>
                <span class="saas-pill pill-violet">{user_dict.get('plan_name', 'Creator Pro')}</span>
                <span style="color: #64748B; font-size: 0.9rem;">/ {current_page}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; gap: 0.5rem; margin-top: 4px;">
                <span class="saas-pill pill-emerald" style="font-size: 0.82rem; padding: 0.25rem 0.75rem;">
                    ⚡ {credit_balance} Credits Available
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; gap: 0.5rem; margin-top: 4px;">
                <span style="font-weight: 600; font-size: 0.9rem;">👤 {user_dict.get('username', 'Creator')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border: none; border-bottom: 1px solid #23273D;'/>", unsafe_allow_html=True)

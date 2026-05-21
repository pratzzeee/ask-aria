APPLE_CSS = """
<style>
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display',
                 'Inter', 'Helvetica Neue', sans-serif !important;
}

header[data-testid="stHeader"] { display: none; }

.block-container {
    padding-top: 2rem !important;
    max-width: 820px !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    border-radius: 14px !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.75rem !important;
}

[data-testid="stChatMessage"] p {
    font-size: 16px !important;
    line-height: 1.7 !important;
}

/* ── Input bar ── */
[data-testid="stChatInput"] textarea {
    border-radius: 14px !important;
    font-size: 16px !important;
    padding: 0.875rem 1rem !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    width: 100% !important;
    padding: 0.6rem 1rem !important;
    transition: opacity 0.15s ease !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    border-radius: 10px !important;
    font-size: 15px !important;
}

/* ── Slider ── */
[data-testid="stSlider"] p {
    font-size: 15px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] p {
    font-size: 15px !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-size: 15px !important;
}

/* ── Radio ── */
[data-testid="stRadio"] label {
    font-size: 15px !important;
}
[data-testid="stRadio"] label p {
    font-size: 15px !important;
}

/* ── Sidebar text ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    font-size: 15px !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p {
    font-size: 15px !important;
}
</style>
"""

LOGO_HTML = """
<div style="display:flex;align-items:center;gap:12px;margin-bottom:1.5rem;">
    <div style="width:36px;height:36px;background:#1d1d1f;border-radius:10px;
                display:flex;align-items:center;justify-content:center;
                flex-shrink:0;">
        <span style="color:#fff;font-size:18px;font-weight:600;">A</span>
    </div>
    <div>
        <p style="margin:0;font-size:17px;font-weight:500;">Aria</p>
        <p style="margin:0;font-size:13px;opacity:0.5;">Customer Support AI</p>
    </div>
</div>
"""

HEADER_HTML = """
<div style="text-align:center;padding:1.5rem 0 1rem;">
    <div style="width:64px;height:64px;background:#1d1d1f;border-radius:18px;
                display:inline-flex;align-items:center;justify-content:center;
                margin-bottom:16px;">
        <span style="color:#fff;font-size:30px;font-weight:600;">A</span>
    </div>
    <h1 style="font-size:32px;font-weight:600;margin:0 0 6px;letter-spacing:-0.5px;">
        How can I help you?
    </h1>
    <p style="font-size:16px;opacity:0.5;margin:0;">
        Ask me anything or upload a document to get started.
    </p>
</div>
"""

LABEL_HTML = '<p style="font-size:12px;opacity:0.45;text-transform:uppercase;letter-spacing:0.07em;margin:16px 0 6px;">{}</p>'

TECH_STACK_HTML = """
<div style="font-size:13px;opacity:0.45;line-height:2;">
    <p style="margin:0;text-transform:uppercase;letter-spacing:0.07em;
              font-size:12px;margin-bottom:4px;">Built with</p>
    <span>LLaMA 3 · Groq · Pinecone</span><br>
    <span>HuggingFace · Streamlit</span>
</div>
"""

def footer_html(name, github, linkedin):
    return f"""
<div style="text-align:center;padding:2rem 0 1.5rem;">
    <p style="font-size:13px;opacity:0.45;margin:0;">
        Built by
        <a href="{github}" target="_blank"
           style="text-decoration:none;font-weight:500;opacity:1;">{name}</a>
        ·
        <a href="{linkedin}" target="_blank"
           style="text-decoration:none;font-weight:500;">LinkedIn</a>
    </p>
</div>
"""

def suggestion_card_html(icon, title, subtitle):
    return f"""
<div style="border-radius:14px;padding:18px 20px;
            margin-bottom:12px;
            border:1px solid rgba(128,128,128,0.2);
            background:rgba(128,128,128,0.05);">
    <p style="font-size:24px;margin:0 0 8px;">{icon}</p>
    <p style="font-size:15px;font-weight:500;margin:0 0 4px;">{title}</p>
    <p style="font-size:14px;opacity:0.5;margin:0;line-height:1.4;">{subtitle}</p>
</div>
"""
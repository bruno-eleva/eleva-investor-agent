"""
Eleva AI - Investor Data Room Assistant
"""

import json
import streamlit as st
from dotenv import load_dotenv
import os
import base64
import anthropic

load_dotenv()

# ── Load data room content at module level (runs once on import) ──
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(APP_DIR, "data_room_cache.json")

DATA_ROOM_CONTENT = ""
try:
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        DATA_ROOM_CONTENT = json.load(f).get("content", "")
except Exception:
    DATA_ROOM_CONTENT = ""

# ── Load logo at module level ──
LOGO_BASE64 = None
try:
    logo_path = os.path.join(APP_DIR, "assets", "eleva-logo.png")
    with open(logo_path, "rb") as f:
        LOGO_BASE64 = base64.b64encode(f.read()).decode()
except Exception:
    pass

# ── Get API key ──
def _get_anthropic_key():
    try:
        return st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    except Exception:
        return os.getenv("ANTHROPIC_API_KEY")

# ── Claude call helper ──
def ask_claude(system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
    key = _get_anthropic_key()
    if not key:
        return "Service temporarily unavailable."
    client = anthropic.Anthropic(api_key=key)
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


SYSTEM_QA = """You are the Eleva AI Data Room Assistant. Your role is to help investors
get accurate answers based on the company's official data room documentation.

GUIDELINES:
1. Use the exact terminology, phrasing, and tone from the data room.
2. Structure responses clearly with headings, bullet points, and lists.
3. Only include information explicitly stated in or directly inferred from the data room.
4. When relevant, reference which section the information comes from.
5. Maintain a confident, professional tone appropriate for investor relations.
6. If information is missing, clearly state what is available and what would need to be addressed separately.

You have access to the complete Eleva AI Data Room content below."""

SYSTEM_DOC = """You are the Eleva AI Data Room Assistant generating formal investor documents.

Your task is to:
1. Parse the provided text to identify all questions (they may be organized by categories)
2. Answer each question using ONLY information from the data room
3. Generate a professional, well-structured document ready to send to investors

GUIDELINES:
- Preserve the category structure if questions are organized by sections.
- Use the exact terminology and tone from the data room.
- Only include information explicitly stated in the data room.
- Maintain a confident, professional tone.
- If information is missing, note that additional details can be provided upon request.

Output a complete, polished document in Markdown format."""


# ── Page config ──
st.set_page_config(
    page_title="Eleva AI - Investor Portal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ──
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    .main { padding-top: 1rem; max-width: 900px; margin: 0 auto; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 900px; }

    .hero-section { text-align: center; padding: 3rem 2rem; margin-bottom: 2rem; }
    .logo-container { margin-bottom: 1.5rem; }
    .logo-container img { height: 50px; width: auto; }
    .hero-subtitle { font-size: 1.1rem; font-weight: 500; color: #3a3a3a; margin-bottom: 1rem; letter-spacing: 0.5px; }
    .hero-description { font-size: 1rem; color: #666; max-width: 500px; margin: 0 auto; line-height: 1.6; }

    .stTextArea textarea { font-size: 1rem; border-radius: 12px; border: 1px solid #e0e0e0; padding: 1rem; }
    .stTextArea textarea:focus { border-color: #3a3a3a; box-shadow: 0 0 0 1px #3a3a3a; }
    .stTextInput input { border-radius: 12px; border: 1px solid #e0e0e0; }

    .time-info { background: #f8f9fa; border-radius: 10px; padding: 1rem 1.5rem; margin: 1rem 0; text-align: center; color: #666; font-size: 0.95rem; }

    .stButton > button { background: #3a3a3a; color: white; border: none; border-radius: 10px; padding: 0.75rem 2rem; font-weight: 500; font-size: 1rem; transition: all 0.2s ease; }
    .stButton > button:hover { background: #2a2a2a; color: white; transform: translateY(-1px); }

    .stDownloadButton > button { background: transparent; color: #3a3a3a; border: 1px solid #3a3a3a; border-radius: 10px; font-weight: 500; }
    .stDownloadButton > button:hover { background: #f8f9fa; color: #3a3a3a; }

    .stTabs [data-baseweb="tab-list"] { gap: 2rem; justify-content: center; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 500; color: #666; padding: 1rem 0; }
    .stTabs [aria-selected="true"] { color: #3a3a3a; }

    .section-header { text-align: center; margin-bottom: 1.5rem; }
    .section-header h3 { color: #3a3a3a; font-size: 1.4rem; font-weight: 600; margin-bottom: 0.5rem; }
    .section-header p { color: #666; font-size: 1rem; }

    .footer-section { text-align: center; color: #999; font-size: 0.85rem; margin-top: 4rem; padding-top: 2rem; border-top: 1px solid #eee; }
    .footer-section p { margin: 0.3rem 0; }

    div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Header ──
if LOGO_BASE64:
    logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" alt="Eleva">'
else:
    logo_html = '<span style="font-size: 2rem; font-weight: 700; color: #3a3a3a;">eleva</span>'

st.markdown(f"""
<div class="hero-section">
    <div class="logo-container">
        {logo_html}
    </div>
    <p class="hero-subtitle">Investor Data Room Assistant</p>
    <p class="hero-description">
        Get instant answers to your questions about Eleva AI.<br>
        All responses are based on our official documentation.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Check data is loaded ──
if not DATA_ROOM_CONTENT:
    st.error("Data room content is not available. Please try again later.")
    st.stop()


# ── Main interface ──
tab1, tab2 = st.tabs(["💬  Ask a Question", "📄  Due Diligence Report"])

with tab1:
    st.markdown("""
    <div class="section-header">
        <h3>What would you like to know?</h3>
        <p>Ask any question about Eleva AI — business model, traction, team, market, and more.</p>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area(
        "Your Question",
        placeholder="Example: What is Eleva AI's revenue model and current traction?",
        height=120,
        label_visibility="collapsed"
    )

    st.markdown('<div class="time-info">Responses typically take 15-30 seconds</div>', unsafe_allow_html=True)

    if st.button("Get Answer", type="primary", use_container_width=True):
        if question:
            with st.spinner("Analyzing your question..."):
                try:
                    response = ask_claude(
                        SYSTEM_QA,
                        f"DATA ROOM CONTENT:\n{DATA_ROOM_CONTENT}\n\n---\n\nINVESTOR QUESTION:\n{question}\n\nProvide a professional response based on the data room content.",
                    )
                    st.markdown("---")
                    st.markdown("### Answer")
                    st.markdown(response)
                    st.download_button(
                        "📥 Download Response", response,
                        file_name="eleva_ai_response.md", mime="text/markdown",
                        use_container_width=True
                    )
                except Exception:
                    st.error("Unable to generate response. Please try again.")
        else:
            st.warning("Please enter your question above.")

with tab2:
    st.markdown("""
    <div class="section-header">
        <h3>Generate a Due Diligence Report</h3>
        <p>Paste your list of questions and receive a comprehensive document addressing each one.</p>
    </div>
    """, unsafe_allow_html=True)

    doc_title = st.text_input(
        "Report Title",
        value="Eleva AI - Due Diligence Response",
        placeholder="Enter a title for your report"
    )

    questions_text = st.text_area(
        "Your Questions", height=300,
        placeholder="""Paste your questions here. You can organize them by category:

PRODUCT & MARKET
- What problem does Eleva AI solve?
- What is your competitive advantage?

TRACTION & METRICS
- What is your current revenue?
- What are your key growth metrics?

TEAM & VISION
- Who are the founders?
- What is your long-term vision?""",
        label_visibility="collapsed"
    )

    st.markdown('<div class="time-info">Comprehensive reports typically take 1-2 minutes</div>', unsafe_allow_html=True)

    if st.button("Generate Report", type="primary", use_container_width=True, key="generate"):
        if questions_text.strip():
            with st.spinner("Generating your comprehensive report..."):
                try:
                    document = ask_claude(
                        SYSTEM_DOC,
                        f"DATA ROOM CONTENT:\n{DATA_ROOM_CONTENT}\n\n---\n\nDOCUMENT REQUEST:\nTitle: {doc_title}\n\nQUESTIONS:\n{questions_text}\n\nGenerate a professional investor document addressing all questions, preserving category structure.",
                        max_tokens=8192
                    )
                    st.markdown("---")
                    st.markdown("### Your Report")
                    st.markdown(document)
                    st.download_button(
                        "📥 Download Report", document,
                        file_name=f"{doc_title.replace(' ', '_')}.md", mime="text/markdown",
                        use_container_width=True
                    )
                except Exception:
                    st.error("Unable to generate report. Please try again.")
        else:
            st.warning("Please paste your questions above.")

# ── Footer ──
st.markdown("""
<div class="footer-section">
    <p>All information is based on Eleva AI's official data room documentation.</p>
    <p>For additional inquiries, contact the Eleva AI team directly.</p>
</div>
""", unsafe_allow_html=True)

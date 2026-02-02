"""
Eleva AI - Investor Data Room Assistant
"""

import streamlit as st
from dotenv import load_dotenv
import os
import base64

from agent import ElevaDataRoomAgent

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Eleva AI - Investor Portal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_logo_base64():
    """Load logo as base64 for embedding."""
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "eleva-logo.png")
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

LOGO_BASE64 = get_logo_base64()

# Professional CSS matching Eleva brand
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Import clean font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container */
    .main {
        padding-top: 1rem;
        max-width: 900px;
        margin: 0 auto;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }

    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
    }

    .logo-container {
        margin-bottom: 1.5rem;
    }

    .logo-container img {
        height: 50px;
        width: auto;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 500;
        color: #3a3a3a;
        margin-bottom: 1rem;
        letter-spacing: 0.5px;
    }

    .hero-description {
        font-size: 1rem;
        color: #666;
        max-width: 500px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Loading container */
    .loading-section {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 4rem 2rem;
        margin: 2rem auto;
        text-align: center;
        max-width: 700px;
    }

    .loading-section h2 {
        color: #3a3a3a;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    .loading-section p {
        color: #666;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }

    .loading-section .subtext {
        color: #999;
        font-size: 0.9rem;
    }

    /* Form elements */
    .stTextArea textarea {
        font-size: 1rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        padding: 1rem;
    }

    .stTextArea textarea:focus {
        border-color: #3a3a3a;
        box-shadow: 0 0 0 1px #3a3a3a;
    }

    .stTextInput input {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
    }

    /* Time info box */
    .time-info {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        text-align: center;
        color: #666;
        font-size: 0.95rem;
    }

    /* Response container */
    .response-container {
        background-color: #f8f9fa;
        border-left: 3px solid #3a3a3a;
        padding: 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 1.5rem 0;
    }

    /* Buttons */
    .stButton > button {
        background: #3a3a3a;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #2a2a2a;
        color: white;
        transform: translateY(-1px);
    }

    .stDownloadButton > button {
        background: transparent;
        color: #3a3a3a;
        border: 1px solid #3a3a3a;
        border-radius: 10px;
        font-weight: 500;
    }

    .stDownloadButton > button:hover {
        background: #f8f9fa;
        color: #3a3a3a;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 500;
        color: #666;
        padding: 1rem 0;
    }

    .stTabs [aria-selected="true"] {
        color: #3a3a3a;
    }

    /* Section headers */
    .section-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .section-header h3 {
        color: #3a3a3a;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .section-header p {
        color: #666;
        font-size: 1rem;
    }

    /* Footer */
    .footer-section {
        text-align: center;
        color: #999;
        font-size: 0.85rem;
        margin-top: 4rem;
        padding-top: 2rem;
        border-top: 1px solid #eee;
    }

    .footer-section p {
        margin: 0.3rem 0;
    }

    /* Hide streamlit elements */
    div[data-testid="stDecoration"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


def get_agent():
    """Initialize the agent with secrets or environment variables."""
    try:
        notion_key = st.secrets.get("NOTION_API_KEY") or os.getenv("NOTION_API_KEY")
        anthropic_key = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        page_id = st.secrets.get("NOTION_ROOT_PAGE_ID") or os.getenv("NOTION_ROOT_PAGE_ID", "1c978b84590d80d48509e1585e9ff849")
    except:
        notion_key = os.getenv("NOTION_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        page_id = os.getenv("NOTION_ROOT_PAGE_ID", "1c978b84590d80d48509e1585e9ff849")

    if not notion_key or not anthropic_key:
        return None

    return ElevaDataRoomAgent(
        anthropic_api_key=anthropic_key,
        notion_api_key=notion_key,
        notion_root_page_id=page_id
    )


def render_header():
    """Render the header with logo."""
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


def render_loading():
    """Render the loading screen."""
    if LOGO_BASE64:
        logo_html = f'<img src="data:image/png;base64,{LOGO_BASE64}" alt="Eleva" style="height: 45px; margin-bottom: 1rem;">'
    else:
        logo_html = '<span style="font-size: 1.8rem; font-weight: 700; color: #3a3a3a;">eleva</span>'

    st.markdown(f"""
    <div class="hero-section">
        <div class="logo-container">
            {logo_html}
        </div>
        <p class="hero-subtitle">Investor Data Room Assistant</p>
    </div>

    <div class="loading-section">
        <h2>Preparing Your Experience</h2>
        <p>Loading the latest information from our data room...</p>
        <p class="subtext">This may take a moment on first load</p>
    </div>
    """, unsafe_allow_html=True)


def main():
    # Initialize agent
    if "agent" not in st.session_state:
        agent = get_agent()
        if agent is None:
            st.error("Service temporarily unavailable. Please try again later.")
            return
        st.session_state.agent = agent

    # Load data room content
    if "data_loaded" not in st.session_state:
        render_loading()

        with st.spinner(""):
            try:
                st.session_state.agent.load_data_room()
                st.session_state.data_loaded = True
                st.rerun()
            except Exception as e:
                st.error("Unable to load data room. Please refresh the page or try again later.")
                return

    # Render header
    render_header()

    # Main interface
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

        st.markdown("""
        <div class="time-info">
            ⏱️ Responses typically take 15-30 seconds
        </div>
        """, unsafe_allow_html=True)

        if st.button("Get Answer", type="primary", use_container_width=True):
            if question:
                with st.spinner("Analyzing your question..."):
                    try:
                        response = st.session_state.agent.answer_question(question)
                        st.markdown("---")
                        st.markdown("### Answer")
                        st.markdown(response)

                        st.download_button(
                            "📥 Download Response",
                            response,
                            file_name="eleva_ai_response.md",
                            mime="text/markdown",
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
            "Your Questions",
            height=300,
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

        st.markdown("""
        <div class="time-info">
            ⏱️ Comprehensive reports typically take 1-2 minutes
        </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Report", type="primary", use_container_width=True, key="generate"):
            if questions_text.strip():
                with st.spinner("Generating your comprehensive report..."):
                    try:
                        document = st.session_state.agent.generate_document_from_text(
                            questions_text=questions_text,
                            document_title=doc_title
                        )
                        st.markdown("---")
                        st.markdown("### Your Report")
                        st.markdown(document)

                        st.download_button(
                            "📥 Download Report",
                            document,
                            file_name=f"{doc_title.replace(' ', '_')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    except Exception:
                        st.error("Unable to generate report. Please try again.")
            else:
                st.warning("Please paste your questions above.")

    # Footer
    st.markdown("""
    <div class="footer-section">
        <p>All information is based on Eleva AI's official data room documentation.</p>
        <p>For additional inquiries, contact the Eleva AI team directly.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

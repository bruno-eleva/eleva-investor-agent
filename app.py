"""
Eleva AI - Investor Data Room Assistant
"""

import streamlit as st
from dotenv import load_dotenv
import os

from agent import ElevaDataRoomAgent

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Eleva AI - Investor Portal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS for investors
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main styling */
    .main {
        padding-top: 2rem;
    }

    .hero-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 1rem;
    }

    .hero-description {
        font-size: 1rem;
        color: #888;
        max-width: 600px;
        margin: 0 auto;
    }

    .stTextArea textarea {
        font-size: 1rem;
        border-radius: 10px;
    }

    .stTextInput input {
        border-radius: 10px;
    }

    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        text-align: center;
    }

    .info-box p {
        margin: 0;
        font-size: 0.95rem;
    }

    .response-container {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 1.5rem 0;
    }

    .loading-container {
        text-align: center;
        padding: 3rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        border-radius: 16px;
        margin: 2rem 0;
    }

    .loading-container h2 {
        color: #1a1a2e;
        margin-bottom: 1rem;
    }

    .loading-container p {
        color: #666;
        font-size: 1.1rem;
    }

    .tab-content {
        padding: 1.5rem 0;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: transform 0.2s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        color: white;
    }

    .footer-note {
        text-align: center;
        color: #999;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


def get_agent():
    """Initialize the agent with secrets or environment variables."""
    # Try Streamlit secrets first (for cloud deployment), then env variables
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


def main():
    # Hero Header
    st.markdown("""
    <div class="hero-header">
        <p class="hero-title">🚀 Eleva AI</p>
        <p class="hero-subtitle">Investor Data Room Assistant</p>
        <p class="hero-description">
            Get instant answers to your questions about Eleva AI.
            All responses are based on our official documentation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize agent
    if "agent" not in st.session_state:
        agent = get_agent()
        if agent is None:
            st.error("Service temporarily unavailable. Please try again later.")
            return
        st.session_state.agent = agent

    # Load data room content
    if "data_loaded" not in st.session_state:
        st.markdown("""
        <div class="loading-container">
            <h2>Preparing Your Experience</h2>
            <p>Loading the latest information from our data room...</p>
            <p style="font-size: 0.9rem; color: #888;">This may take a moment on first load.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.spinner(""):
            try:
                st.session_state.agent.load_data_room()
                st.session_state.data_loaded = True
                st.rerun()
            except Exception as e:
                st.error("Unable to load data room. Please refresh the page or try again later.")
                return

    # Main interface
    tab1, tab2 = st.tabs(["💬 Ask a Question", "📄 Due Diligence Report"])

    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown("### What would you like to know?")
        st.markdown("Ask any question about Eleva AI - our business model, traction, team, market opportunity, and more.")

        question = st.text_area(
            "Your Question",
            placeholder="Example: What is Eleva AI's revenue model and current traction?",
            height=100,
            label_visibility="collapsed"
        )

        st.markdown("""
        <div class="info-box">
            <p>⏱️ Responses typically take 15-30 seconds</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Get Answer", type="primary", use_container_width=True):
            if question:
                with st.spinner("Analyzing your question..."):
                    try:
                        response = st.session_state.agent.answer_question(question)
                        st.markdown("### Answer")
                        st.markdown(f'<div class="response-container">{response}</div>', unsafe_allow_html=True)

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

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)

        st.markdown("### Generate a Due Diligence Report")
        st.markdown("Paste your list of questions and receive a comprehensive document addressing each one.")

        doc_title = st.text_input(
            "Report Title",
            value="Eleva AI - Due Diligence Response",
            placeholder="Enter a title for your report"
        )

        questions_text = st.text_area(
            "Your Questions",
            height=350,
            placeholder="""Paste your questions here. You can organize them by category:

PRODUCT & MARKET
- What problem does Eleva AI solve?
- What is your competitive advantage?
- Who are your target customers?

TRACTION & METRICS
- What is your current revenue?
- How many active users do you have?
- What are your key growth metrics?

TEAM & VISION
- Who are the founders?
- What is your long-term vision?
- What are you planning to do with the investment?""",
            label_visibility="collapsed"
        )

        st.markdown("""
        <div class="info-box">
            <p>⏱️ Comprehensive reports typically take 1-2 minutes</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Report", type="primary", use_container_width=True):
            if questions_text.strip():
                with st.spinner("Generating your comprehensive report..."):
                    try:
                        document = st.session_state.agent.generate_document_from_text(
                            questions_text=questions_text,
                            document_title=doc_title
                        )
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

        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer-note">
        <p>All information provided is based on Eleva AI's official data room documentation.</p>
        <p>For additional inquiries, please contact the Eleva AI team directly.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

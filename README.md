# Eleva AI Data Room Agent

An intelligent agent that answers investor questions using your Notion data room content. Maintains the same structure, terminology, and professional tone as your official documentation.

## Quick Start

### 1. Install Dependencies

```bash
cd eleva-agent
pip install -r requirements.txt
```

### 2. Set Up Notion Integration

1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **"+ New integration"**
3. Name it (e.g., "Eleva Data Room Agent")
4. Select your workspace
5. Copy the **Internal Integration Secret**

### 3. Connect Integration to Data Room

1. Open your data room in Notion
2. Click **"..."** (top right) → **"Connections"**
3. Add your integration
4. Repeat for all child pages you want accessible

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```
NOTION_API_KEY=ntn_xxxxxxxxxxxxx
NOTION_ROOT_PAGE_ID=1c978b84590d80d48509e1585e9ff849
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 5. Run the Agent

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Features

### Quick Q&A Mode
Ask individual investor questions and get immediate, professionally formatted responses.

### Document Generation
Generate formal documents addressing multiple questions at once—perfect for due diligence responses or investor updates.

### Data Room Overview
Get a summary of your data room's structure and key content areas.

## Usage Tips

- **Refresh Data**: Click "Refresh Data Room" in the sidebar after updating Notion
- **Be Specific**: More specific questions yield more precise answers
- **Add Context**: Use the context field to specify the audience or situation
- **Download Responses**: All responses can be downloaded as Markdown

## Programmatic Usage

```python
from agent import ElevaDataRoomAgent

agent = ElevaDataRoomAgent(
    anthropic_api_key="sk-ant-...",
    notion_api_key="ntn_...",
    notion_root_page_id="1c978b84590d80d48509e1585e9ff849"
)

# Load data room
agent.load_data_room()

# Answer a question
response = agent.answer_question("What is Eleva AI's revenue model?")

# Generate a document
document = agent.generate_document(
    questions=[
        "What is the market opportunity?",
        "Who are the key competitors?",
        "What is the go-to-market strategy?"
    ],
    document_title="Series A Due Diligence Response"
)
```

## Troubleshooting

**"Failed to load data room"**
- Ensure your Notion integration has access to all pages
- Check that the page ID is correct
- Verify your API keys are valid

**Missing content from subpages**
- Each page must be explicitly shared with the integration
- Go to each subpage → Connections → Add integration

**Rate limiting**
- The agent caches content to minimize API calls
- Use "Refresh Data Room" only when content has changed

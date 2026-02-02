"""
Eleva AI Data Room Agent
Answers investor questions using the same structure and language as the data room.
"""

import anthropic
from notion_client_helper import NotionDataRoom
from typing import Optional


class ElevaDataRoomAgent:
    def __init__(
        self,
        anthropic_api_key: str,
        notion_api_key: str,
        notion_root_page_id: str,
        model: str = "claude-sonnet-4-20250514"
    ):
        self.anthropic = anthropic.Anthropic(api_key=anthropic_api_key)
        self.notion = NotionDataRoom(notion_api_key, notion_root_page_id)
        self.model = model
        self._data_room_content: Optional[str] = None

    def load_data_room(self, force_refresh: bool = False) -> str:
        """Load all content from the Notion data room."""
        if self._data_room_content and not force_refresh:
            return self._data_room_content

        if force_refresh:
            self.notion.clear_cache()

        self._data_room_content = self.notion.get_full_data_room_content()
        return self._data_room_content

    def answer_question(self, question: str, context: Optional[str] = None) -> str:
        """
        Answer a question based on the data room content.
        Uses the same structure and language as the data room.
        """
        if not self._data_room_content:
            self.load_data_room()

        system_prompt = """You are the Eleva AI Data Room Assistant. Your role is to help the CEO
quickly answer investor questions by providing accurate, professional responses based on the
company's official data room documentation.

CRITICAL GUIDELINES:

1. **Use Data Room Language**: Always use the exact terminology, phrasing, and tone from the
   data room. Mirror the professional style and structure of the original documents.

2. **Structure Your Responses**: Format answers in a clear, professional manner suitable for
   investor communications. Use headings, bullet points, and numbered lists as appropriate.

3. **Be Precise**: Only include information that is explicitly stated in or can be directly
   inferred from the data room content. Never fabricate or assume information.

4. **Cite Sections**: When relevant, reference which section of the data room the information
   comes from (e.g., "As outlined in our Financial Projections section...").

5. **Professional Tone**: Maintain a confident, clear, and professional tone appropriate for
   investor relations.

6. **If Information is Missing**: If the data room doesn't contain information to fully answer
   a question, clearly state what is available and what would need to be addressed separately.

You have access to the complete Eleva AI Data Room content below."""

        user_message = f"""DATA ROOM CONTENT:
{self._data_room_content}

---

INVESTOR QUESTION:
{question}

{f'ADDITIONAL CONTEXT: {context}' if context else ''}

Please provide a professional response based on the data room content. Use the same language
and structure as the data room documents."""

        response = self.anthropic.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text

    def generate_document(
        self,
        questions: list[str],
        document_title: str = "Investor Q&A Response",
        include_intro: bool = True
    ) -> str:
        """
        Generate a formal document answering multiple investor questions.
        """
        if not self._data_room_content:
            self.load_data_room()

        questions_formatted = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))

        system_prompt = """You are the Eleva AI Data Room Assistant helping the CEO prepare
formal investor communication documents. Generate professional, well-structured documents that
answer investor questions using the exact language, terminology, and style from the data room.

Your output should be a complete, polished document ready to send to investors."""

        user_message = f"""DATA ROOM CONTENT:
{self._data_room_content}

---

DOCUMENT REQUEST:
Title: {document_title}

Questions to Address:
{questions_formatted}

Please generate a professional document that:
1. Uses a formal structure with clear sections
2. Addresses each question thoroughly using data room content
3. Maintains consistent language and tone with the data room
4. Includes an introduction if appropriate
5. Is ready to share with investors

Format the document in Markdown for easy conversion to other formats."""

        response = self.anthropic.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text

    def generate_document_from_text(
        self,
        questions_text: str,
        document_title: str = "Investor Q&A Response"
    ) -> str:
        """
        Generate a formal document from a raw text block containing questions.
        The model will interpret categories, questions, and structure automatically.
        """
        if not self._data_room_content:
            self.load_data_room()

        system_prompt = """You are the Eleva AI Data Room Assistant helping the CEO prepare
formal investor communication documents.

Your task is to:
1. Parse the provided text to identify all questions (they may be organized by categories/sections)
2. Answer each question using ONLY information from the data room
3. Generate a professional, well-structured document ready to send to investors

CRITICAL GUIDELINES:

- **Preserve Structure**: If the questions are organized by categories (e.g., "PRODUCT-PROBLEM FIT",
  "TRACCIÓN / RETENCIÓN"), maintain that same organization in your response.

- **Use Data Room Language**: Always use the exact terminology, phrasing, and tone from the
  data room. Mirror the professional style of the original documents.

- **Be Precise**: Only include information explicitly stated in or directly inferable from
  the data room. Never fabricate information.

- **Professional Tone**: Maintain a confident, clear tone appropriate for investor relations.

- **Missing Information**: If the data room doesn't contain information to answer a specific
  question, indicate what information is available and note that additional details can be
  provided upon request.

Your output should be a complete, polished document in Markdown format."""

        user_message = f"""DATA ROOM CONTENT:
{self._data_room_content}

---

DOCUMENT REQUEST:
Title: {document_title}

QUESTIONS TO ADDRESS (interpret the structure and answer each one):
{questions_text}

---

Generate a professional investor document that addresses all the questions above,
preserving the category structure if present. Use the same language and terminology
as the data room."""

        response = self.anthropic.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        return response.content[0].text

    def get_data_room_summary(self) -> str:
        """Get a summary of the data room structure and contents."""
        if not self._data_room_content:
            self.load_data_room()

        system_prompt = """Provide a brief executive summary of the data room's structure
and key content areas. List the main sections and what information each contains."""

        response = self.anthropic.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Summarize this data room:\n\n{self._data_room_content}"}
            ]
        )

        return response.content[0].text

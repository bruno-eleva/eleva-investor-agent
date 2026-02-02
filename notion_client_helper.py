"""
Notion Client Helper for Eleva AI Data Room
Fetches and processes content from the Notion data room.
"""

from notion_client import Client
from typing import Optional


class NotionDataRoom:
    def __init__(self, api_key: str, root_page_id: str):
        self.client = Client(auth=api_key)
        self.root_page_id = root_page_id
        self._content_cache: dict = {}

    def get_page_content(self, page_id: str) -> dict:
        """Fetch a single page's content and metadata."""
        if page_id in self._content_cache:
            return self._content_cache[page_id]

        page = self.client.pages.retrieve(page_id=page_id)
        blocks = self._get_all_blocks(page_id)

        content = {
            "id": page_id,
            "title": self._extract_title(page),
            "blocks": blocks,
            "text": self._blocks_to_text(blocks),
        }

        self._content_cache[page_id] = content
        return content

    def _get_all_blocks(self, block_id: str) -> list:
        """Recursively fetch all blocks from a page."""
        blocks = []
        cursor = None

        while True:
            response = self.client.blocks.children.list(
                block_id=block_id,
                start_cursor=cursor,
                page_size=100
            )

            for block in response["results"]:
                blocks.append(block)
                if block.get("has_children"):
                    block["children"] = self._get_all_blocks(block["id"])

            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")

        return blocks

    def _extract_title(self, page: dict) -> str:
        """Extract title from page properties."""
        props = page.get("properties", {})

        if "title" in props:
            title_prop = props["title"]
            if "title" in title_prop and title_prop["title"]:
                return title_prop["title"][0].get("plain_text", "Untitled")

        if "Name" in props:
            name_prop = props["Name"]
            if "title" in name_prop and name_prop["title"]:
                return name_prop["title"][0].get("plain_text", "Untitled")

        return "Untitled"

    def _blocks_to_text(self, blocks: list, indent: int = 0) -> str:
        """Convert blocks to readable text format."""
        text_parts = []
        prefix = "  " * indent

        for block in blocks:
            block_type = block.get("type")

            if block_type == "paragraph":
                text = self._rich_text_to_plain(block.get("paragraph", {}).get("rich_text", []))
                if text:
                    text_parts.append(f"{prefix}{text}")

            elif block_type in ["heading_1", "heading_2", "heading_3"]:
                text = self._rich_text_to_plain(block.get(block_type, {}).get("rich_text", []))
                level = int(block_type[-1])
                marker = "#" * level
                text_parts.append(f"\n{prefix}{marker} {text}")

            elif block_type == "bulleted_list_item":
                text = self._rich_text_to_plain(block.get("bulleted_list_item", {}).get("rich_text", []))
                text_parts.append(f"{prefix}• {text}")

            elif block_type == "numbered_list_item":
                text = self._rich_text_to_plain(block.get("numbered_list_item", {}).get("rich_text", []))
                text_parts.append(f"{prefix}1. {text}")

            elif block_type == "toggle":
                text = self._rich_text_to_plain(block.get("toggle", {}).get("rich_text", []))
                text_parts.append(f"{prefix}▸ {text}")

            elif block_type == "quote":
                text = self._rich_text_to_plain(block.get("quote", {}).get("rich_text", []))
                text_parts.append(f"{prefix}> {text}")

            elif block_type == "callout":
                text = self._rich_text_to_plain(block.get("callout", {}).get("rich_text", []))
                icon = block.get("callout", {}).get("icon", {}).get("emoji", "💡")
                text_parts.append(f"{prefix}{icon} {text}")

            elif block_type == "code":
                text = self._rich_text_to_plain(block.get("code", {}).get("rich_text", []))
                lang = block.get("code", {}).get("language", "")
                text_parts.append(f"{prefix}```{lang}\n{text}\n{prefix}```")

            elif block_type == "divider":
                text_parts.append(f"{prefix}---")

            elif block_type == "table":
                table_text = self._table_to_text(block)
                text_parts.append(f"{prefix}{table_text}")

            elif block_type == "child_page":
                title = block.get("child_page", {}).get("title", "Untitled")
                text_parts.append(f"{prefix}📄 [{title}]")

            elif block_type == "child_database":
                title = block.get("child_database", {}).get("title", "Untitled Database")
                text_parts.append(f"{prefix}📊 [{title}]")

            # Process children recursively
            if "children" in block:
                child_text = self._blocks_to_text(block["children"], indent + 1)
                if child_text:
                    text_parts.append(child_text)

        return "\n".join(text_parts)

    def _rich_text_to_plain(self, rich_text: list) -> str:
        """Convert Notion rich text to plain text."""
        return "".join(item.get("plain_text", "") for item in rich_text)

    def _table_to_text(self, block: dict) -> str:
        """Convert table block to text format."""
        if "children" not in block:
            return "[Table]"

        rows = []
        for row_block in block.get("children", []):
            if row_block.get("type") == "table_row":
                cells = row_block.get("table_row", {}).get("cells", [])
                row_text = " | ".join(self._rich_text_to_plain(cell) for cell in cells)
                rows.append(row_text)

        return "\n".join(rows)

    def get_all_pages(self) -> list[dict]:
        """Fetch all pages in the data room recursively."""
        pages = []
        self._collect_pages(self.root_page_id, pages)
        return pages

    def _collect_pages(self, page_id: str, pages: list, depth: int = 0):
        """Recursively collect all pages."""
        if depth > 10:  # Prevent infinite recursion
            return

        try:
            content = self.get_page_content(page_id)
            pages.append(content)

            # Find child pages in blocks
            for block in content.get("blocks", []):
                if block.get("type") == "child_page":
                    child_id = block.get("id")
                    if child_id:
                        self._collect_pages(child_id, pages, depth + 1)

        except Exception as e:
            print(f"Error fetching page {page_id}: {e}")

    def get_full_data_room_content(self) -> str:
        """Get all content from the data room as a single text."""
        pages = self.get_all_pages()

        sections = []
        for page in pages:
            section = f"\n{'='*60}\n"
            section += f"# {page['title']}\n"
            section += f"{'='*60}\n\n"
            section += page['text']
            sections.append(section)

        return "\n\n".join(sections)

    def clear_cache(self):
        """Clear the content cache."""
        self._content_cache.clear()

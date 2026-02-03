#!/usr/bin/env python3
"""
Refresh the data room cache.
Fetches all content from Notion and saves it to a local JSON file.
Run manually or via GitHub Actions on a schedule.
"""

import json
import os
import sys
from datetime import datetime, timezone

from notion_client_helper import NotionDataRoom


def main():
    notion_key = os.getenv("NOTION_API_KEY")
    page_id = os.getenv("NOTION_ROOT_PAGE_ID", "1c978b84590d80d48509e1585e9ff849")

    if not notion_key:
        print("Error: NOTION_API_KEY not set")
        sys.exit(1)

    print("Fetching data room content from Notion...")
    notion = NotionDataRoom(notion_key, page_id)
    pages = notion.get_all_pages()

    # Build the cached content
    sections = []
    for page in pages:
        section = f"\n{'='*60}\n"
        section += f"# {page['title']}\n"
        section += f"{'='*60}\n\n"
        section += page['text']
        sections.append(section)

    full_content = "\n\n".join(sections)

    cache_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "page_count": len(pages),
        "content": full_content,
    }

    cache_path = os.path.join(os.path.dirname(__file__), "data_room_cache.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

    print(f"Cache saved: {len(pages)} pages, {len(full_content)} characters")
    print(f"Last updated: {cache_data['last_updated']}")


if __name__ == "__main__":
    main()

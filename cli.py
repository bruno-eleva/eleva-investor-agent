#!/usr/bin/env python3
"""
Eleva AI Data Room Agent - Command Line Interface
Quick access to the agent from terminal.
"""

import argparse
import os
import sys
from dotenv import load_dotenv

from agent import ElevaDataRoomAgent


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Eleva AI Data Room Agent - Answer investor questions"
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="The question to answer"
    )
    parser.add_argument(
        "-c", "--context",
        help="Additional context for the question"
    )
    parser.add_argument(
        "-o", "--output",
        help="Save response to file"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show data room summary instead of answering a question"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force refresh data room content"
    )

    args = parser.parse_args()

    # Check for API keys
    notion_key = os.getenv("NOTION_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    page_id = os.getenv("NOTION_ROOT_PAGE_ID", "1c978b84590d80d48509e1585e9ff849")

    if not notion_key or not anthropic_key:
        print("Error: Missing API keys. Set NOTION_API_KEY and ANTHROPIC_API_KEY in .env")
        sys.exit(1)

    # Initialize agent
    print("Initializing agent...")
    agent = ElevaDataRoomAgent(
        anthropic_api_key=anthropic_key,
        notion_api_key=notion_key,
        notion_root_page_id=page_id
    )

    print("Loading data room content...")
    agent.load_data_room(force_refresh=args.refresh)

    if args.summary:
        print("\n--- Data Room Summary ---\n")
        response = agent.get_data_room_summary()
    elif args.question:
        print(f"\n--- Answering: {args.question} ---\n")
        response = agent.answer_question(args.question, args.context)
    else:
        # Interactive mode
        print("\nEleva AI Data Room Agent - Interactive Mode")
        print("Type 'quit' to exit, 'summary' for overview\n")

        while True:
            try:
                question = input("Question: ").strip()

                if question.lower() == 'quit':
                    break
                elif question.lower() == 'summary':
                    print("\n" + agent.get_data_room_summary() + "\n")
                elif question:
                    print("\n" + agent.answer_question(question) + "\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

        return

    print(response)

    if args.output:
        with open(args.output, "w") as f:
            f.write(response)
        print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()

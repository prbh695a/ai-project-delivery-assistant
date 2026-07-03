from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

from exporter import export_project_summaries_to_excel
from genai_assistant import analyze_project, render_insights_markdown
from mapper import (
    build_project_summary,
    extract_ticket,
    group_tickets_by_project,
    ticket_from_csv_row,
)
from openproject_client import OpenProjectClient


BASE_DIR = Path(__file__).resolve().parent.parent


def load_config(path: str = "config/config.example.yaml") -> dict[str, Any]:
    config_path = BASE_DIR / path
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_demo_tickets() -> list[dict[str, Any]]:
    sample_path = BASE_DIR / "sample_data" / "sample_tickets.csv"
    with open(sample_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return [ticket_from_csv_row(row) for row in reader]


def load_openproject_tickets(config: dict[str, Any]) -> list[dict[str, Any]]:
    api_key = os.getenv("OPENPROJECT_API_KEY")
    if not api_key:
        raise RuntimeError("OPENPROJECT_API_KEY is missing in .env file")

    op_config = config["openproject"]
    ca_bundle = op_config.get("ca_bundle")
    verify_ssl: bool | str = op_config.get("verify_ssl", True)
    if ca_bundle:
        verify_ssl = str(BASE_DIR / ca_bundle)

    client = OpenProjectClient(
        base_url=op_config["base_url"],
        api_key=api_key,
        verify_ssl=verify_ssl,
    )

    raw_work_packages = client.get_work_packages(
        project_identifier=op_config["project_identifier"]
    )

    return [
        extract_ticket(
            raw_ticket=wp,
            project_id_custom_field=op_config["project_id_custom_field"],
        )
        for wp in raw_work_packages
    ]


def create_project_summaries(tickets: list[dict[str, Any]], config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped, exceptions = group_tickets_by_project(tickets)

    project_summaries = []
    for project_id, project_tickets in grouped.items():
        summary = build_project_summary(
            project_id=project_id,
            tickets=project_tickets,
            closed_statuses=config["sync"]["closed_statuses"],
            blocked_statuses=config["sync"]["blocked_statuses"],
            max_lines=config["sync"]["max_ticket_lines_per_project"],
        )
        project_summaries.append(summary)

    return project_summaries, exceptions


def main() -> None:
    parser = argparse.ArgumentParser(description="AI-assisted project delivery tracker demo")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use anonymized sample_data/sample_tickets.csv instead of OpenProject API.",
    )
    parser.add_argument(
        "--config",
        default="config/config.example.yaml",
        help="Path to YAML config relative to repository root.",
    )
    args = parser.parse_args()

    load_dotenv(BASE_DIR / ".env")
    config = load_config(args.config)

    tickets = load_demo_tickets() if args.demo else load_openproject_tickets(config)
    project_summaries, exceptions = create_project_summaries(tickets, config)

    output_excel = BASE_DIR / config["output"]["excel_file"]
    output_insights = BASE_DIR / config["output"]["insights_file"]

    export_project_summaries_to_excel(project_summaries, output_excel)

    insights = [analyze_project(summary) for summary in project_summaries]
    output_insights.parent.mkdir(parents=True, exist_ok=True)
    output_insights.write_text(render_insights_markdown(insights), encoding="utf-8")

    print(f"Tickets processed: {len(tickets)}")
    print(f"Projects found: {len(project_summaries)}")
    print(f"Tickets without Project ID: {len(exceptions)}")
    print(f"Excel summary created: {output_excel}")
    print(f"AI delivery insights created: {output_insights}")

    if exceptions:
        print("\nExceptions:")
        for exception in exceptions:
            print(f"- {exception['type']}: OP#{exception['ticket_id']} - {exception['subject']}")


if __name__ == "__main__":
    main()
